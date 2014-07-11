from django.core.management.base import BaseCommand, CommandError
from watson.metric import Metrics

class Command(BaseCommand):

    def handle(self, *args, **options):
        if not args:
            raise CommandError('Command requires file name on input')
        self.stdout.write('Loading file: %s' % args[0])
        out = Metrics.import_from_file(args[0])
        self.stdout.write("\n".join(out))