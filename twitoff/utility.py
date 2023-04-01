from io import BytesIO
from flask import send_file


def fig_response(fig):
    """Turn a matplotlib Figure into Flask response"""
    img_bytes = BytesIO()
    fig.savefig(img_bytes)
    img_bytes.seek(0)
    return send_file(img_bytes, mimetype='image/png')


def nocache(response):
    """Add Cache-Control headers to disable caching a response"""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate,'\
                                        ' max-age=0'
    return response
