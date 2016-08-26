#! /usr/bin/env python
import os, re
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

def new_folder(path):
    print('Create folder %s' % path)
    ret = requests.post(BASE_URL+'/api/new-folder', data={'path':path})
    if not ret.ok:
        raise Exception(ret.reason)

def copy_file(path, dest):
    print('Copying %s to %s' % (path, dest))
    ext = os.path.splitext(path)[1].lower()
    if not ext in ['.py']:
        print('Cannot transfert [%s] files, use ftp for the moment' % ext)
    else:
        ret = requests.post(BASE_URL+'/api/save', data={'path':dest, 'content':open(path, 'r').read()})

def run_file(path):
    ret = requests.post(BASE_URL+'/api/run', data={'path':path})
    print(ret)


def call_project(args):
    if args.action == 'list':
        print('\n'.join(get_projects_list()))
    if args.action == 'new':
        # Ensure the projects doesn't exist already
        projectName = args.params[0]
        if projectName in get_projects_list():
            raise Exception('Project %s already exists' % projectName)
        # Create the folder
        new_folder(os.path.join('projects', projectName))
    if args.action == 'deploy':
        path = args.params[0]
        proj = os.path.basename(os.path.normpath(path))
        if not os.path.isdir(path):
            raise Exception("Path must target a project's folder")

        # Ensure project exists
        if not proj in get_projects_list():
            raise Exception('Project %s does not exist' % proj)
        
        print('Deploying project %s' % proj)
        for (fName, fSub, files) in os.walk(path):
            # Copy the files
            for f in files:
                copy_file(os.path.join(fName, f), os.path.join('projects', proj, os.path.relpath(fName, start=path), f))
            # Create subfolder
            for f in fSub:
                new_folder(os.path.join('projects', proj, f))

    if args.action == 'run':
        proj = args.params[0]
        # Ensure project exists
        if not proj in get_projects_list():
            raise Exception('Project %s does not exist' % proj)

        # Execute main.py inside the project
        run_file(os.path.join('projects', proj, 'main.py'))


def call_script(args):
    pass


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='''QPython Web Editor command line client
    ''')
    subparsers = arg_parser.add_subparsers(dest='cmd')
    subparsers.required = True

    parser_project = subparsers.add_parser('project')
    parser_project.add_argument('action', choices=['new', 'deploy', 'list', 'run'])
    parser_project.add_argument('params', nargs='*')
    parser_project.set_defaults(func=call_project)

    parser_script = subparsers.add_parser('script')
    parser_script.set_defaults(func=call_script)

    # parser.add_argument('category', choices=['project', 'script'], nargs=1)
    # parser.add_argument('action', choices=['newproject', 'deploy', 'run'])
    # parser.add_argument('params', nargs='*')
    # parser.add_argument('--project')

    args = arg_parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
        print(e)
