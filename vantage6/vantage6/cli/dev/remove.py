import subprocess
import itertools
from shutil import rmtree
from pathlib import Path

import click

from vantage6.common import info
from vantage6.cli.context import ServerContext, NodeContext
from vantage6.cli.server.common import click_insert_context
from vantage6.cli.server.remove import cli_server_remove
from vantage6.cli.utils import remove_file


@click.command()
@click_insert_context
@click.pass_context
def remove_demo_network(
    click_ctx: click.Context, ctx: ServerContext
) -> None:
    """ Remove all related demo network files and folders.

    Select a server configuration to remove that server and the nodes attached
    to it.
    """

    # remove the server
    for handler in itertools.chain(ctx.log.handlers, ctx.log.root.handlers):
        handler.close()
    click_ctx.invoke(cli_server_remove, ctx=ctx, force=True)

    # removing the server import config
    info("Deleting demo import config file")
    server_configs = ServerContext.instance_folders("server", ctx.name,
                                                    system_folders=False)
    import_config_to_del = Path(server_configs['dev']) / f"{ctx.name}.yaml"
    remove_file(import_config_to_del, 'import_configuration')

    # also remove the server folder
    server_configs = ServerContext.instance_folders("server", ctx.name,
                                                    system_folders=True)
    server_folder = server_configs['data']
    if server_folder.is_dir():
        rmtree(server_folder)

    # remove the nodes
    configs, _ = NodeContext.available_configurations(system_folders=False)
    node_names = [
        config.name for config in configs if f'{ctx.name}_node_' in config.name
    ]
    for name in node_names:
        node_ctx = NodeContext(name, False)
        for handler in itertools.chain(node_ctx.log.handlers,
                                       node_ctx.log.root.handlers):
            handler.close()
        subprocess.run(
            ["v6", "node", "remove", "-n", name, "--user", "--force"]
        )

    # remove data files attached to the network
    data_dirs_nodes = NodeContext.instance_folders('node', '', False)['dev']
    rmtree(Path(data_dirs_nodes / ctx.name))
