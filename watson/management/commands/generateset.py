from optparse import make_option
import json
from django.core.management.base import BaseCommand, CommandError
from watson.generator import Generator


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-s', '--session', action='store', type='string', dest='session_name',
                    help='Sets session name from which learning set is generated'),
        make_option('-o', '--output', action='store', type='string', dest='output_file',
                    help='Sets output file name, on default session name is used'),
        make_option('-m', '--metrics', action='store', type='string', dest='metrics_filter',
                    help='Sets metrics that should be included in result'),
        make_option('-u', '--users', action='store', type='int', dest='user_lower_bound',
                    help='Sets minimal number of same answers for users for the article to be returned'),
        make_option('-n', '--number', action='store', type='int', dest='limit',
                    help='Sets size, on default session size is used'),
        make_option('-b', '--hub', action='store', type='string', dest='hub_filter',
                    help='Sets hub for which learning set will be generated'),
        make_option('-q', '--quality', action='store', type='int', dest='quality_filter',
                    help='Sets minimal quality for which learning set will be generated'),
    )

    def handle(self, *args, **options):
        if not options['session_name']:
            raise CommandError('At least session name has to be stated')
        generator = Generator(session=options['session_name'])
        if options['metrics_filter']:
            metrics = options['metrics_filter'].split(',')
            for metric in metrics:
                generator.set_metric(metric)
        if options['user_lower_bound'] is not None:
            generator.set_lower_bound(options['user_lower_bound'])
        if options['limit'] is not None:
            generator.set_limit(options['limit'])
        if options['hub_filter']:
            generator.set_hub_filter(options['hub_filter'])
        if options['quality_filter'] is not None:
            generator.set_quality_filter(options['quality_filter'])

        output = options['output_file'] if options['output_file'] else "%s.json" % options['session_name']
        results = generator.run()
        self.stdout.write("Found %d items" % len(results))
        if results:
            with open(output, 'w') as outfile:
                json.dump(results, outfile)
                outfile.close()