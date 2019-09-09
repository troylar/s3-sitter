from s3_sitter import s3_sitter
import click
import json
import yaml


@click.group()
def cli():
    pass


@cli.command()
@click.option('--buckets', '-b', default="")
@click.option('--keys', '-k', default="")
def check(buckets, keys):
    keys_j = json.loads(keys)
    sitter = s3_sitter(Buckets=buckets, Keys=keys_j)
    sitter.check_all_buckets()
    sitter.check_all_keys()


@cli.command()
@click.argument('function_name')
@click.option('--buckets', '-b', default="")
@click.option('--keys', '-k', default="")
def write_resources(buckets, keys, function_name):
    iam_resources = []
    for b in buckets.split(','):
        iam_resources.append('arn:aws:s3:::{}'.format(b))

    for k in keys.split(','):
        iam_resources.append('arn:aws:s3:::{}'.format(k))
        sitter = s3_sitter(Buckets=buckets, Keys=keys_j)

    with open('./{}_resources.yml'.format(function_name), 'w') as outfile:
        yaml.dump(iam_resources, outfile)

if __name__ == '__main__':
    cli()
