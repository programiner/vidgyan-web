from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

def fetch_video_info(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'extract_flat': False,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    formats = info.get('formats', [])
    video_formats = {}
    audio_formats = []
    
    preferred_resolutions = ['360p', '480p', '720p', '1080p']
    selected_m4a = None  # Store one M4A format

    for fmt in formats:
        format_id = fmt.get('format_id', 'N/A')
        resolution = fmt.get('format_note', 'Unknown')
        ext = fmt.get('ext', 'N/A')
        acodec = fmt.get('acodec', 'none')
        vcodec = fmt.get('vcodec', 'none')
        url = fmt.get('url', '')

        sound_icon = "🔊" if acodec != 'none' else "🔇"

        # ✅ Store all MP4 formats (With & Without Sound)
        if vcodec != 'none' and ext == 'mp4':
            key = f"{resolution}-{ext}-{sound_icon}"
            if key not in video_formats:
                video_formats[key] = {
                    'format_id': format_id,
                    'url': url,
                    'resolution': f"{resolution} {sound_icon}",
                    'ext': ext,
                    'acodec': acodec,
                    'type': 'video_with_audio' if acodec != 'none' else 'video_only'
                }

        # ✅ Only one M4A format
        elif acodec != 'none' and vcodec == 'none' and ext == 'm4a' and selected_m4a is None:
            selected_m4a = {
                'format_id': format_id,
                'url': url,
                'ext': ext,
                'type': 'audio_only'
            }

    video_list = list(video_formats.values())

    # ✅ Sort: Sound wale pehle, phir Preferred Resolutions
    video_list.sort(key=lambda x: x['acodec'] == 'none')

    # ✅ Sirf **360p, 480p, 720p, 1080p ya higher** wale formats include karo
    selected_videos = []
    seen_resolutions = set()

    for video in video_list:
        base_res = video['resolution'].split()[0]
        if base_res in preferred_resolutions and base_res not in seen_resolutions:
            selected_videos.append(video)
            seen_resolutions.add(base_res)

    return {
        'title': info.get('title', 'Unknown'),
        'thumbnail': info.get('thumbnail', ''),
        'resolutions': selected_videos,
        'audio_formats': [selected_m4a] if selected_m4a else []  # ✅ Only 1 M4A format
    }

@app.route('/fetch_video', methods=['POST'])
def fetch_video():
    try:
        data = request.get_json()
        url = data.get('url')
        if not url:
            return jsonify({'error': 'URL is required!'}), 400

        video_info = fetch_video_info(url)
        return jsonify(video_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__': 
    app.run(debug=True, port=5000)
