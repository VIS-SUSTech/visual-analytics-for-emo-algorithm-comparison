from flask import Flask, escape, abort, request
from flask_cors import CORS
from urllib.parse import unquote
import json, traceback
import numpy as np

from graph import calc_graph
from sampler import sampler

server = Flask(__name__)
data_dir = './data'
CORS(server, resources=r'/*')

@server.route('/')
def home():
  return '<p>EvoX VisSystem Data Server</p>'

@server.route('/info/<name>')
def info(name: str):
  try:
    with open(f'{data_dir}/{escape(name)}/index.json') as fc:
      config = json.load(fc)
    res = {
      **config['info'],
      'algorithms': len(config['algorithms'])
    }
    return res
  except Exception as e:
    print(e)
    abort(404)

@server.route('/data/<name>')
def data(name: str):
  try:
    with open(f'{data_dir}/{escape(name)}/index.json') as fc:
      config = json.load(fc)
    res = { 'data' : {} }
    for alg, file in config['algorithms'].items():
      with open('%s/%s/%s/%s' % (data_dir, escape(name), config['display'], file)) as fd:
        res['data'][alg] = json.load(fd)
    with open('%s/%s/%s/%s' % (data_dir, escape(name), config['display'], config['reference'])) as fp:
      res['data']['PF'] = json.load(fp)
    with open(f'{data_dir}/{escape(name)}/runs_similarity.json') as fs:
      res['similarity'] = dict(json.load(fs))
    res['pfCluster'] = np.ones(len(res['data']['PF'])).tolist()
    return res
  except Exception as e:
    print(e)
    abort(404)

@server.route('/obj_vec/<name>/<path:algorithm>/<frame>')
def obj_vec(name: str, algorithm: str, frame: str):
  try:
    with open(f'{data_dir}/{escape(name)}/index.json') as fc:
      config = json.load(fc)
    with open('%s/%s/%s/%s' % (data_dir, escape(name), config['origin'], config['algorithms'][escape(algorithm)])) as fd:
      res = json.load(fd)['result']['obj'][escape(frame)]
    return res
  except Exception as e:
    print(e)
    abort(404)

@server.route('/attachment/<name>/<path:algorithm>')
def attachment(name: str, algorithm: str):
  try:
    with open(f'{data_dir}/{escape(name)}/index.json') as fc:
      config = json.load(fc)
    file = config['attachments'][escape(algorithm)]
    with open('%s/%s/%s/%s' % (data_dir, escape(name), config['attach'], file)) as fd:
      res = json.load(fd)
    return res
  except Exception as e:
    print(e)
    abort(404)

@server.route('/graph/<name>', methods=['POST'])
def graph(name: str):
  try:
    origin_algorithms = request.get_json()
    formater = lambda x: unquote(x).replace('/', '').replace('-', '')
    algorithms = list(map(formater, origin_algorithms))
    with open(f'{data_dir}/{escape(name)}/index.json') as fc:
      config = json.load(fc)
    src = []
    for algA in algorithms:
      t = []
      for algB in algorithms:
        with open('%s/%s/%s/%s' % (data_dir, escape(name), config['distance'], f'{algA}_{algB}_{escape(name)}_distance.json')) as fd:
          t.append(json.load(fd))
      src.append(t)
    res = calc_graph(src, origin_algorithms)
    return res
  except Exception as e:
    print(e)
    abort(404)

@server.route('/sampling', methods=['POST'])
def sampling():
  try:
    payload = request.get_json() #in the form of {algorithmName: iter}
    algoData = payload['data']
    problem = payload['problem']
    iteration = payload['iteration']
    sampling_rate = payload['sampling_rate']
    if not algoData:
      return {}
    with open(f'{data_dir}/{escape(problem)}/index.json') as fc:
      config = json.load(fc)
    originData = {}
    for algorithm, frame in iteration.items():
      with open('%s/%s/%s/%s' % (data_dir, escape(problem), config['origin'], config['algorithms'][escape(algorithm)])) as fd:
        originData[algorithm] = json.load(fd)['result']['obj'][escape(frame)]
    indices = sampler(algoData, originData, sampling_rate=sampling_rate)
    res = {}
    for algo, _ in algoData.items():
      res[algo] = indices[:len(algoData[algo])].tolist()
      indices = indices[len(algoData[algo]):]
    return res
  except Exception as e:
    print(e)
    abort(404)

@server.errorhandler(404)
def not_found(error):
  print(traceback.format_exc())
  return '<p>Required Resource not Found</p>', 404


if __name__ == '__main__':
  server.run(port=5100)
