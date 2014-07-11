from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from watson.exporter import Exporter

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('-s', '--session', action='store', type='string', dest='session_name', default=None,
                    help='Sets session name from which data will be exported'),
    )

    def handle(self, *args, **options):
        exporter = Exporter(options['session_name'])
        exporter.run()