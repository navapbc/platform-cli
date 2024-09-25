# platform/cli.py
import click

@click.group()
def cli():
    pass

@click.command()
@click.option('--name', default='world', help='Who to greet.')
def greet(name):
    click.echo(f"Hello, {name}!")

@click.command()
def info():
    click.echo("Platform CLI Tool v0.1.0")

cli.add_command(greet)
cli.add_command(info)

if __name__ == '__main__':
    cli()
