
import subprocess
import re
import datetime

if __name__ == '__main__':

    video_urls = [
        'http://nordond7a-f.akamaihd.net/i/wo/open/1c/1c4cb6221812b628895a60f4b558558b54d3356f/e868542a-a718-4c2e-8d24-6eba420934a0_,563,1266,2250,.mp4.csmil/master.m3u8',
        'http://nordond18c-f.akamaihd.net/i/wo/open/5c/5c324cf0d64b3bd05f0981b2a30f925342274151/a064ce52-8f51-4fcf-87a4-f322867d4645_,563,1266,2250,.mp4.csmil/master.m3u8',

        'http://nordond7c-f.akamaihd.net/i/wo/open/69/699424b65f3aba65b2aab2f17280223ed81281c0/ac68d98d-90ed-48ed-b2d8-cafc36cdb195_,141,316,563,1266,2250,.mp4.csmil/master.m3u8',
        'http://nordond25b-f.akamaihd.net/i/wo/open/83/835d4fcc9e5ba8d9ee73a87beca9d63770dcf9a1/4505513e-1452-424f-8456-1dd8ab0d04c4_,141,316,563,1266,2250,.mp4.csmil/master.m3u8'
        ]
    mp4_filenames = ['test1.mp4', 'test2.mp4']

    cmd = ['ffmpeg', '-y', '-stats', '-i', video_urls[0]]
    cmd += ['-c:v', 'copy', '-c:a', 'copy', '-bsf:a', 'aac_adtstoasc', mp4_filenames[0]]

    proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)
    print('After Popen')

    duration = progress = None

    for line in iter(proc.stderr.readline, ''):
        duration_match = re.match('\s+Duration: ([\d:.]+)', line)
        if duration_match:
            duration_list = duration_match.group(1).split(':')
            duration = datetime.timedelta(hours=int(duration_list[0]),
                                          minutes=int(duration_list[1]),
                                          seconds=float(duration_list[2]))

        progress_match = re.match('.+\s+time=([\d:.]+)', line)
        if progress_match:
            progress_list = progress_match.group(1).split(':')
            progress = datetime.timedelta(hours=int(progress_list[0]),
                                          minutes=int(progress_list[1]),
                                          seconds=float(progress_list[2]))

        if duration and progress:
            print('Progress: {:3.4}%'.format(progress/duration*100))

        print(line.rstrip())

    print('Before wait')
    proc.wait()
    print('After wait')

    print('Duration: {}'.format(duration))
