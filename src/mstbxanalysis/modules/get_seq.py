import click
import os
import warnings
from Bio import SeqIO
from Bio.PDB import PDBList
from Bio import Entrez
import pandas as pd
import numpy as np
import time

warnings.filterwarnings("ignore")

def pdb_to_seq(target, seqfile, header):
    for record in SeqIO.parse(target, "pdb-atom"):
        with open(seqfile, "w") as f:
            f.write(">"+header+"\n")
            f.write(str(record.seq))
        return record.seq # Return first record found

def get_pdb(pdbID, format):
    pdbl = PDBList()
    pdbl.retrieve_pdb_file(pdbID, pdir=".", file_format=format, overwrite=True, obsolete=False)
    # Bio.PDB might name it differently depending on format
    # Typically: pdb{id}.ent for pdb format
    if format == 'pdb':
        old_name = f"pdb{pdbID.lower()}.ent"
        new_name = f"pdb{pdbID.lower()}.pdb"
        if os.path.exists(old_name):
            os.rename(old_name, new_name)
            return new_name
    return None

def make_remote_blastp(query, ofile, top, entrez=None, db="nr", e_val=10E-24):
    click.echo(f"Performing Remote BLASTp for {query}...")
    if entrez:
        command = (f"blastp -out remote_blastp_{ofile}.tab -outfmt 7 "
                   f"-query {query} -db {db} -evalue {e_val} -max_target_seqs {top} "
                   f"-remote -entrez_query {entrez} -qcov_hsp_perc 90")
    else:
        command = (f"blastp -out remote_blastp_{ofile}.tab -outfmt 7 "
                   f"-query {query} -db {db} -evalue {e_val} -max_target_seqs {top} "
                   f"-remote -qcov_hsp_perc 90")
    os.system(command)

def filter_blastp_data(file):
    base = os.path.splitext(file)[0]
    fix_tab = f"{base}_fix.tab"
    fix_csv = f"{base}_fix.csv"
    
    os.system(f"grep -v '#' {file} > {fix_tab}")
    if os.path.getsize(fix_tab) == 0:
        click.echo(f"No results found in {file}")
        return np.array([])

    df = pd.read_table(fix_tab, usecols=[0, 1, 2, 10], header=None)
    df.columns = ["QueryNameOgrn", "SeqID", "%Identity", "E-value"]
    df1 = df[df["%Identity"] >= 80]
    df1.to_csv(fix_csv, sep=",", index=False)

    click.echo(f"Retrieved {len(df1)} SeqIDs from {file}")
    return df1["SeqID"].values

def get_seqs(email, SeqIDList, odir):
    Entrez.email = email
    if not os.path.exists(odir):
        os.makedirs(odir)

    count = 1
    incr = 50
    for SeqID in SeqIDList:
        click.echo(f"Downloading SeqID #{count} with ID {SeqID}")
        try:
            handle = Entrez.efetch(db="protein", id=SeqID, rettype="fasta")
            record = SeqIO.read(handle, "fasta")
            SeqIO.write(record, os.path.join(odir, f"{SeqID}.fasta"), "fasta")
            count += 1
        except Exception as e:
            click.echo(f"Error downloading {SeqID}: {e}")

        if count % incr == 0:
            click.echo("Waiting to respect NCBI rate limits...")
            time.sleep(60)

@click.command()
@click.option('--email', required=True, help='Email for NCBI Entrez.')
@click.option('--pdbid', help='PDB ID to download and extract sequence.')
@click.option('--query', help='FASTA file for BLASTp query.')
@click.option('--blast', is_flag=True, help='Run BLASTp.')
@click.option('--db', default='nr', help='BLAST database.')
@click.option('--entrez-query', help='Entrez query for BLAST (e.g., "nematoda[orgn]").')
@click.option('--top', default=20, help='Max target sequences.')
@click.option('--e-val', default=1e-25, help='E-value cutoff.')
@click.option('--odir', default='DownloadedFastas', help='Output directory for fasta files.')
@click.option('--msa-name', default='MSA.fasta', help='Output name for concatenated FASTA.')
def command(email, pdbid, query, blast, db, entrez_query, top, e_val, odir, msa_name):
    """Retrieve sequences from PDB or NCBI via BLASTp."""
    
    current_query = query
    
    if pdbid:
        click.echo(f"Downloading PDB {pdbid}...")
        pdb_file = get_pdb(pdbid, "pdb")
        if pdb_file:
            current_query = f"{pdbid}.fasta"
            pdb_to_seq(pdb_file, current_query, f"PDB {pdbid} extracted sequence")
            click.echo(f"Extracted sequence to {current_query}")

    if blast and current_query:
        ofile_base = "results"
        make_remote_blastp(current_query, ofile_base, top, entrez_query, db, e_val)
        tab_file = f"remote_blastp_{ofile_base}.tab"
        if os.path.exists(tab_file):
            seq_ids = filter_blastp_data(tab_file)
            if len(seq_ids) > 0:
                get_seqs(email, seq_ids, odir)
                # Concat
                click.echo("Concatenating sequences...")
                os.system(f"cat {odir}/*.fasta > {msa_name}")
                os.system(f"seqkit rmdup --by-seq < {msa_name} > {os.path.splitext(msa_name)[0]}_fix.fasta")
                click.echo(f"Final MSA saved to {os.path.splitext(msa_name)[0]}_fix.fasta")

    click.echo("GetSeq process complete.")
