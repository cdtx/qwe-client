#! /usr/bin/env python
import re
import ast    #  abstract syntax trees
import json
import argparse
import requests

BASE_URL = 'http://192.168.1.3:10000'

# def run(**kwargs):
#     if kwargs['action'] == 'newproject':
#         print requests.post(BASE_URL+'/api/new-folder', data={'path':'projects/%s' % kwargs['params'][0]})
# 
#     if kwargs['action'] == 'deploy':
#         ret = requests.post(BASE_URL+'/api/save', data={'path':'projects/%s/%s' % (kwargs['project'], kwargs['params'][0]), 'content':open(kwargs['params'][0], 'r').read()})
#         print ret.reason
# 
#     if kwargs['action'] == 'run':
#         print requests.post(BASE_URL+'/api/run', data={'path':'projects/%s/main.py' % kwargs['project']})

def fix_dict(bad):
    good = bad
    # Returned dict is nor enclosed
    good = "{%s}" % good.replace('\"', '\'')

    # Returned dict can be wrongly formated
    good = re.sub(r",(\w+):", r",'\1':", good)
    return good

def get_projects_list():
    ret = requests.get(BASE_URL+'/api/file-tree')
    content = ret.content.decode()
    projects_list = ast.literal_eval(fix_dict(content))['projects']
    projects_list = [k for k in projects_list['content'].keys() if projects_list['content'][k]['type']=='folder']
    return projects_list

def call_project(args):
    if args.action == 'list':
        print('\n'.join(get_projects_list()))

def call_script(args):
    pass


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='''QPython Web Editor command line client
    ''')
    subparsers = arg_parser.add_subparsers()

    parser_project = subparsers.add_parser('project')
    parser_project.add_argument('action', choices=['new', 'list'])
    parser_project.set_defaults(func=call_project)

    parser_script = subparsers.add_parser('script')
    parser_script.set_defaults(func=call_script)

    # parser.add_argument('category', choices=['project', 'script'], nargs=1)
    # parser.add_argument('action', choices=['newproject', 'deploy', 'run'])
    # parser.add_argument('params', nargs='*')
    # parser.add_argument('--project')

    args = arg_parser.parse_args()
    args.func(args)

