
import moviepy.editor as mp

fileName = "piano_master"

my_clip=mp.VideoFileClip("{}.mp4".format(fileName))
my_clip.audio.write_audiofile("{}.mp3".format(fileName))