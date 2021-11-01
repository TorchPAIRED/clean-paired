# python3 run_many_runs rootdir num_runs
import subprocess
import sys


def doit(root_dir, num_runs):
    import subprocess, os
    my_env = os.environ.copy()
    my_env["PATH"] = "/usr/sbin:/sbin:" + my_env["PATH"]

    for run_id in range(int(num_runs)):
        run_root_dir = root_dir + str(run_id)
        import io

        proc = subprocess.Popen(f"python3 /data/paired_complexity_exps/clean-paired/social_rl/adversarial_env/train_adversarial_env.py --root_dir {run_root_dir}", env=my_env, shell=True, stdout=subprocess.PIPE)
        for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
            print(line)

if __name__ == "__main__":
    doit(sys.argv[1], sys.argv[2])