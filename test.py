
import subprocess
import nrkrecorder
import time

if __name__ == '__main__':

    video_urls = [
        'http://nordond7a-f.akamaihd.net/i/wo/open/1c/1c4cb6221812b628895a60f4b558558b54d3356f/e868542a-a718-4c2e-8d24-6eba420934a0_,563,1266,2250,.mp4.csmil/master.m3u8',
        'http://nordond18c-f.akamaihd.net/i/wo/open/5c/5c324cf0d64b3bd05f0981b2a30f925342274151/a064ce52-8f51-4fcf-87a4-f322867d4645_,563,1266,2250,.mp4.csmil/master.m3u8',

        'http://nordond7c-f.akamaihd.net/i/wo/open/69/699424b65f3aba65b2aab2f17280223ed81281c0/ac68d98d-90ed-48ed-b2d8-cafc36cdb195_,141,316,563,1266,2250,.mp4.csmil/master.m3u8',
        'http://nordond25b-f.akamaihd.net/i/wo/open/83/835d4fcc9e5ba8d9ee73a87beca9d63770dcf9a1/4505513e-1452-424f-8456-1dd8ab0d04c4_,141,316,563,1266,2250,.mp4.csmil/master.m3u8'
        ]
    mp4_filenames = ['test0.mp4', 'test0.mp4']

    i = 0
    cmd = ['ffmpeg', '-loglevel', '8', '-stats', '-y', '-stats', '-i', video_urls[i]]
    cmd += ['-c:v', 'copy', '-c:a', 'copy', '-bsf:a', 'aac_adtstoasc', 'test' + str(i) + '.m4v']

    proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)
    print('Started process')

    while proc.poll() is None:
        seconds = nrkrecorder.utils.ffmpeg_seconds_downloaded(proc)
        print('Downloaded {} seconds'.format(seconds))
        time.sleep(0.5)

    print('Before wait')
    proc.wait()
    print('After wait')
