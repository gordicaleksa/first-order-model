"""
    Wrapper around demo.py used to animate all of the images in mydata/target_imgs dir using specified driver video
    (via driver_video_name argument), that should be placed inside of mydata/driver_videos,
    if not specified '04.mp4' (Donald Trump) is used as a default driver.

    Results are dumped to mydata/output_dir/

    Note: make sure you have ffmpeg.exe in your system PATH.
"""

import os
import subprocess
import time
import argparse
import shutil

if __name__ == "__main__":
    #
    # fixed args - don't change these unless you have a good reason (vox-cpk is most suitable for portrait animation)
    #
    data_root = os.path.join(os.path.dirname(__file__), 'mydata')
    driver_videos_root = os.path.join(data_root, 'driver_videos')
    target_images_root = os.path.join(data_root, 'target_imgs')
    output_videos_root = os.path.join(data_root, 'output_dir')
    os.makedirs(output_videos_root, exist_ok=True)
    model_path = os.path.join(os.path.dirname(__file__), 'checkpoints', 'vox-cpk.pth.tar')

    #
    # modifiable args - feel free to play with these
    #
    parser = argparse.ArgumentParser()
    parser.add_argument("--driver_video_name", type=str, help="video to drive target images", default='04.mp4')
    args = parser.parse_args()

    ffmpeg = 'ffmpeg.exe'
    if not shutil.which(ffmpeg):
        print(f'{ffmpeg} not found in the system path, aborting.')

    driver_video_path = os.path.join(driver_videos_root, args.driver_video_name)

    for img_name in os.listdir(target_images_root):
        target_img_path = os.path.join(target_images_root, img_name)
        # out video is named after image it's animating
        out_video_path = os.path.join(output_videos_root, img_name.split('.')[0] + '.mp4')

        ts = time.time()
        print(f'Animating {img_name}.')
        try:
            # dumps animated video at 'out_video_path' (no sound)
            subprocess.call(['python', 'demo.py', '--config', 'config/vox-256.yaml', '--driving_video', driver_video_path,
                             '--source_image', target_img_path, '--checkpoint', model_path,
                             '--result_video', out_video_path,
                             '--relative', '--adapt_scale'])
            print(f'Done animating, animated video placed at {out_video_path}.')

            # dump audio from driver video
            driver_video_audio_path = os.path.join(output_videos_root, 'tmp.aac')
            subprocess.call([ffmpeg, '-y', '-i', driver_video_path, '-vn', '-c:a', 'copy', driver_video_audio_path])
            print(f'Dumped driver video audio at {driver_video_audio_path}.')

            # check if audio was actually dumped (not the most elegant solution - but it does the job)
            if os.path.exists(driver_video_audio_path):
                base, old_name = os.path.split(out_video_path)
                new_name = old_name.split('.')[0] + '_sound.mp4'
                final_video_with_audio_path = os.path.join(base, new_name)
                subprocess.call([ffmpeg, '-i', out_video_path, '-i', driver_video_audio_path, '-c:v', 'copy', '-c:a', 'copy', final_video_with_audio_path])
                print(f'Merged animated video and driver video audio at {final_video_with_audio_path}.')

                os.remove(out_video_path)
                print(f'Deleting version without sound {out_video_path}.')
                os.remove(driver_video_audio_path)
                print(f'Deleting tmp audio file {driver_video_audio_path}.')
            else:
                print(f'Driver video {driver_video_path} has no audio, skipping merge between animated video and driver video audio.')
        except Exception as e:
            print(f'Skipping {img_name}.')
            print(f'Got this exception {e}.')

        print(f'Time took {(time.time()-ts)} secs.')
