# python3 run_many_runs rootdir num_runs
import subprocess
import sys


def doit(root_dir, num_runs):
    for run_id in range(int(num_runs)):
        run_root_dir = root_dir + str(run_id)
        subprocess.check_output(f"python3 /data/paired_complexity_exps/clean-paired/social_rl/adversarial_env/train_adversarial_env.py --root_dir {run_root_dir}")

if __name__ == "__main__":
    doit(sys.argv[1], sys.argv[2])