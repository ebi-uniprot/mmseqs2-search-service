from pathlib import Path
import subprocess
import logging
import tempfile
import shutil

class MMSeqsService(object):
    def __init__(self, db_dir, workspace_dir, result_dir):
        """Initialize paths for MMseqs2 service.
        Args:
            db_dir (str): Path to MMseqs2 database directory.
            workspace_dir (str): Path to temporary workspace directory(scratch).
            result_dir (str): Path to results directory in PVC.
        """
        # directory initialised by init pod
        self.db_path = Path(db_dir)
        # local temp workspace
        self.workspace_path = Path(workspace_dir)
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        # pvc
        self.result_path = Path(result_dir)

    def mmseqs2_search(self, job):
        """Run mmseqs easy-search on a FASTA sequence from the job."""
        
        job_id, fasta_content = self.extract_job_id_fasta(job)

        logging.info(f"Processing job_id: {job_id}")

        with tempfile.TemporaryDirectory(dir=self.workspace_path) as tmpdirname:
            temp_dir = Path(tmpdirname)
            query_file = temp_dir / "input.fasta"

            # write FASTA to temp file
            with open(query_file, "w") as f:
                f.write(fasta_content)

            result_file = temp_dir / f"{job_id}.m8"
            cmd = self.prepare_mmseqs_cmd(result_file, temp_dir, query_file)

            try:
                subprocess.run(cmd, check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                logging.error(f"mmseqs easy-search failed: {e.stderr.decode()}")
                raise RuntimeError(f"mmseqs easy-search failed: {e.stderr.decode()}")
            
            # Move the result to results folder
            final_result_file = self.result_path / f"{job_id}.m8"
            shutil.move(str(result_file), final_result_file)
            logging.info(f"Result saved to {final_result_file}")

    
    def extract_job_id_fasta(self, job):
        job_id = job.get("job_id")
        if not job_id:
            raise ValueError("Job must contain a job_id")
        
        logging.info(f"Got job with job_id: {job_id}")
        
        fasta_content = job.get("fasta")

        if not fasta_content:
            raise ValueError("No FASTA content in job")
        
        logging.info(f"FASTA content length: {len(fasta_content)} characters")
        return job_id,fasta_content
    

    
    def prepare_mmseqs_cmd(self, result_file, temp_dir, query_file):
        # This will be created and populated by mmseqs
        mmseqs_tmp_dir = temp_dir / "tmp"

            # build mmseqs easy-search command
        cmd = [
                "mmseqs",
                "easy-search",
                str(query_file),
                str(self.db_path),
                str(result_file),
                str(mmseqs_tmp_dir),
            ]
        
        return cmd
