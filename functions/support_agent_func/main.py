import json, os, sys
here = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, here)

from src.agent.models import CustomerMessage
from src.agent.agent_pipeline import ProductionSupportAgent

agent = ProductionSupportAgent()

def handler(context, basicIO) ->
    method = basicIO.get_request_method()
    if method == 'POST':
        req_str = basicIO.get_request_body()
        data = json.loads(req_str)
        text = data.get('text', '')
        msg = CustomerMessage(id='catalyst_query', text=text)
        out = agent.process(msg)
        basicIO.write(json.dumps(out.to_dict()))
        basicIO.set_status(200)
        context.close()
    else:
        basicIO.write('{"error": "Only POST is supported"}')
        basicIO.set_status(400)
        context.close()
