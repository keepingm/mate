import sys

from flask import Flask, Response, stream_with_context
from flask_cors import CORS

from agent import TestAgentApp

app = Flask(__name__)

CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True
)


@app.route('/run', methods=['GET'])
def run():
    dataset = 'stock'
    agent_app = TestAgentApp(dataset)

    # 直接使用 stream_run，因为它现在已经是 generate json string 了
    response = Response(
        stream_with_context(agent_app.stream_run()),
        mimetype='application/json', # 建议改为 json 或 text/event-stream
        headers={
            'X-Accel-Buffering': 'no',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
        }
    )
    return response

    # def generate():
    #     for chunk in agent_app.stream_run():
    #         yield chunk.content
    #         # 可选：强制刷新
    #         sys.stdout.flush() if hasattr(sys.stdout, 'flush') else None
    #
    # # 关键：设置禁用缓冲的响应头
    # response = Response(
    #     stream_with_context(generate()),
    #     mimetype='text/plain',
    #     headers={
    #         'X-Accel-Buffering': 'no',  # 禁用代理缓冲
    #         'Cache-Control': 'no-cache, no-store, must-revalidate',
    #         'Pragma': 'no-cache',
    #         'Expires': '0',
    #         'Connection': 'keep-alive',
    #     }
    # )

    return response

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
