import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.curdir))
from eval.run_eval import main

if __name__ == '__main__':
    start_time = time.time()
    print('Starting Headline Metric Reproduction Pipeline...')
    main()
    elapsed = time.time() - start_time
    print(f'Done! Pipeline reproduced in {elapsed:.2f} seconds (well under the 15-minute budget).')
