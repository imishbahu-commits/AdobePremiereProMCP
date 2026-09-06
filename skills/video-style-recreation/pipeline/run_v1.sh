#!/bin/bash
# Recreate video-1 style: video render + music bed + VO mix + mux.
set -e
cd "$(dirname "$0")"
FF=./ffmpeg_x64
PL=plates
AS=assets

echo "== probe VO durations"
for f in vo_01.mp3 vo_b.mp3 vo_c.mp3 vo_d.mp3; do
  $FF -hide_banner -i $f 2>&1 | grep Duration | sed "s|^|  $f |"
done

echo "== plates + graph"
PYTHONPATH=/home/user/AdobePremiereProMCP/outputs/pylibs python3 gen_render_v1.py

INPUTS=(
  -loop 1 -i $AS/v1_room.png
  -loop 1 -i $AS/v1_hero_down.png
  -loop 1 -i $AS/v1_hero_up.png
  -loop 1 -i $AS/v1_hamster.png
  -loop 1 -i $AS/v1_bar.png
  -loop 1 -i $AS/v1_box.png
  -loop 1 -i $AS/v1_space.png
  -loop 1 -i $AS/v1_jag.png
)
# numerals 4..18 in rep order (num_8 never used)
for n in 4 5 6 7 9 10 11 12 13 14 15 16 17 18; do
  INPUTS+=(-loop 1 -i $PL/num_$n.png)
done
INPUTS+=(
  -loop 1 -i $PL/ladder.png
  -loop 1 -i $PL/chip_0.png -loop 1 -i $PL/chip_1.png -loop 1 -i $PL/chip_2.png
  -loop 1 -i $PL/chip_3.png -loop 1 -i $PL/chip_4.png
  -loop 1 -i $PL/bubble.png
  -loop 1 -i $PL/burst_a.png -loop 1 -i $PL/burst_b.png
  -loop 1 -i $PL/coupon.png -loop 1 -i $PL/brand.png -loop 1 -i $PL/adtag.png
  -loop 1 -i $PL/title.png -loop 1 -i $PL/goldset.png -loop 1 -i $PL/white.png
  -loop 1 -i $PL/fin.png
)

echo "== render video (silent)"
$FF -y "${INPUTS[@]}" -filter_complex_script filtergraph_v1.txt \
  -map '[out]' -t 78 -r 30 -c:v libx264 -preset fast -crf 20 -an v1_video.mp4 2>&1 | tail -3

echo "== audio mix"
cat > aud_v1.txt <<'AEOF'
[0:a]adelay=1000|1000[va];
[1:a]adelay=30800|30800[vb];
[2:a]adelay=43800|43800[vc];
[3:a]adelay=58200|58200[vd];
[va][vb][vc][vd]amix=4:normalize=0,volume=1.7,acompressor=threshold=0.13:ratio=3:attack=8:release=120,apad=whole_len=3439800[vo];
aevalsrc=exprs='sin(2*PI*(46+52*exp(-mod(t\,0.46875)*30))*t)*exp(-mod(t\,0.46875)*13)*0.80':s=44100:d=78[kick];
aevalsrc=exprs='sin(2*PI*55*t)*0.30*exp(-mod(t\,0.9375)*2.2)':s=44100:d=78[bass];
aevalsrc=exprs='0.045*(sin(2*PI*220*t)+sin(2*PI*261.63*t)+sin(2*PI*329.63*t))*(0.6+0.4*sin(2*PI*0.25*t))':s=44100:d=78[pad];
anoisesrc=d=78:c=white:r=44100:a=0.4,highpass=f=8000,tremolo=f=8:d=0.95,volume=0.22[hats];
[kick][bass][pad][hats]amix=4:normalize=0,volume=0.85[bed];
[vo]asplit=2[voA][voB];
[bed][voA]sidechaincompress=threshold=0.03:ratio=8:attack=25:release=450:makeup=1[duck];
[duck][voB]amix=2:normalize=0,loudnorm=I=-15:TP=-1.5:LRA=9,afade=t=out:st=76:d=2[outa]
AEOF
$FF -y -i vo_01.mp3 -i vo_b.mp3 -i vo_c.mp3 -i vo_d.mp3 \
  -filter_complex_script aud_v1.txt -map '[outa]' -t 78 -c:a aac -b:a 160k v1_audio.m4a 2>&1 | tail -3

echo "== mux"
$FF -y -i v1_video.mp4 -i v1_audio.m4a -map 0:v -map 1:a -c:v copy -c:a aac \
  -movflags +faststart v1_recreation_cut1.mp4 2>&1 | tail -2
$FF -hide_banner -i v1_recreation_cut1.mp4 2>&1 | grep -E "Duration|Stream"

echo "== poster"
$FF -y -hide_banner -loglevel error -ss 67.2 -i v1_recreation_cut1.mp4 -frames:v 1 -q:v 3 server/public/posters/v1_recreation_cut1.jpg
echo "== DONE"
