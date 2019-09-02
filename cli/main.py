from s3_sitter import s3_sitter
import click
import json


@click.command()
@click.option('--buckets', '-b', default=[])
@click.option('--keys', '-k', default="{}")
def main(buckets, keys):
    keys_j = json.loads(keys)
    sitter = s3_sitter(Buckets=buckets, Keys=keys_j)
    sitter.check_all_buckets()
    sitter.check_all_keys()


if __name__ == '__main__':
    main()
