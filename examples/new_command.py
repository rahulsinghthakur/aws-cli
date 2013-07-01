"""
Add a new top-level command
---------------------------

This example adds a new top-level command called config.  We are going
to assume that the config command will have the following subcommands::

    aws config help
    aws config foo
    aws config bar
"""
from awscli.clidriver import BuiltInCommand
from awscli.help import HelpCommand
from awscli.argparser import ServiceArgParser
from bcdoc.clidocs import CLIDocumentEventHandler
import bcdoc.clidocevents


class ConfigDocumentEventHandler(CLIDocumentEventHandler):
    """
    This class registers for the document events we are
    interested in and implements the handlers for those events.
    """

    def initialize(self, session):
        CLIDocumentEventHandler.initialize(self, session)
        session.register('doc-title.Config.*', self.title)
        session.register('doc-description.Config.*', self.description)

    def build_translation_map(self):
        for op in self.service.operations:
            self.translation_map[op.name] = op.cli_name

    def title(self, help_command, **kwargs):
        doc = help_command.doc
        doc.style.h1(help_command.name)

    def description(self, help_command, **kwargs):
        doc = help_command.doc
        config = help_command.obj
        doc.style.h2('Description')
        doc.include_doc_string(config.documentation)


class ConfigHelpCommand(HelpCommand):

    EventHandlerClass = ConfigDocumentEventHandler
    
    @property
    def event_class(self):
        return 'Config'
    
    @property
    def name(self):
        return 'config'

    
class ConfigCommand(BuiltInCommand):

    documentation = "Edit the AWSCLI config file"

    def do_foo(self, remaining_args, parsed_globals):
        print('do foo now')

    def do_bar(self, remaining_args, parsed_globals):
        print('do bar now')

    def __call__(self, args, parsed_globals):
        op_table = self._create_operations_table()
        command_parser = self._create_service_parser(op_table)
        parsed_args, remaining = command_parser.parse_known_args(args)
        return op_table[parsed_args.operation](remaining, parsed_globals)

    def _create_service_parser(self, operation_table):
        return ServiceArgParser(
            operations_table=operation_table, service_name=self.name)

    def _create_operations_table(self):
        op_table = {}
        op_table['foo'] = self.do_foo
        op_table['bar'] = self.do_bar
        op_table['help'] = ConfigHelpCommand(self.session, self,
                                             command_table=op_table,
                                             arg_table=None)
        return op_table
                                                     
def add_command(command_table, session, **kwargs):
    """
    This is our event handler.  It will get called as the top-level
    commands are getting built.  We can add our custom commands to
    the ``command_table``.  To do this, we have to add a callable
    to the ``command_table`` that will get called when our command
    is specified on the command line.
    """
    command_table['config'] = ConfigCommand('config', session)


def awscli_initialize(cli):
    cli.register('building-command-table', handler=add_command)
