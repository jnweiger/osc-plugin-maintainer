#
# osc-plugin-maintainer.py - everything what the builtin maintainer 
# command does, plus it also looks into the changelog.
#
# (C) 2013, jw@suse.de, openSUSE.org
# Distribute under GPLv2 or GPLv3
#
# 2013-01-21, V0.1 - jw@suse.de just an initial idea.
#                    After Karl and Ciaran noted that only the changes 
#                    file really tells who is maintaining a package.

import traceback
global OSC_MAINTAINER_PLUGIN_VERSION, OSC_MAINTAINER_PLUGIN_NAME
OSC_MAINTAINER_PLUGIN_VERSION = '0.01'
OSC_MAINTAINER_PLUGIN_NAME = traceback.extract_stack()[-1][0] + ' V' + OSC_MAINTAINER_PLUGIN_VERSION

# grab a handle to the original implementation
# before we redefine it.
__osc_do_maintainer = do_maintainer

# CAUTION: Keep these decorators in sync with osc/commandline.py:6287ff
##
@cmdln.option('-b', '--bugowner-only', action='store_true',
              help='Show only the bugowner')
@cmdln.option('-B', '--bugowner', action='store_true',
              help='Show only the bugowner if defined, or maintainer otherwise')
@cmdln.option('-e', '--email', action='store_true',
              help='show email addresses instead of user names')
@cmdln.option('--nodevelproject', action='store_true',
              help='do not follow a defined devel project ' \
                   '(primary project where a package is developed)')
@cmdln.option('-v', '--verbose', action='store_true',
              help='show more information')
@cmdln.option('-D', '--devel-project', metavar='devel_project',
              help='define the project where this package is primarily developed')
@cmdln.option('-a', '--add', metavar='user',
              help='add a new person for given role ("maintainer" by default)')
@cmdln.option('-A', '--all', action='store_true',
              help='list all found entries not just the first one')
@cmdln.option('-s', '--set-bugowner', metavar='user',
              help='Set the bugowner to specified person')
@cmdln.option('-S', '--set-bugowner-request', metavar='user',
              help='Set the bugowner to specified person via a request')
@cmdln.option('-d', '--delete', metavar='user',
              help='delete a maintainer/bugowner (can be specified via --role)')
@cmdln.option('-r', '--role', metavar='role', action='append', default=[],
              help='Specify user role')
@cmdln.alias('bugowner')
def do_maintainer(self, subcmd, opts, *args):
        """${cmd_name}: Show maintainers of a project/package

            osc maintainer <options>
            osc maintainer BINARY <options>
            osc maintainer PRJ <options>
            osc maintainer PRJ PKG <options>
    
        The tool looks up the default responsible person for a certain project or package.
        When using with an OBS 2.4 (or later) server it is doing the lookup for
        a given binary according to the server side configuration of default owners.

        PRJ and PKG default to current working-copy path.

        This osc-maintainer plugin also reports the latest few changelog authors.

        ${cmd_usage}
        ${cmd_option_list}
        """
        self.__osc_do_maintainer(subcmd, opts, *args)

        prj = None
        pac = None
        args = slash_split(args)
        if len(args) == 0:
            try:
                pac = store_read_package('.')
            except oscerr.NoWorkingCopy:
                pass
            prj = store_read_project('.')
        elif len(args) == 1:
            # it is unclear if one argument is a binary or a project, try binary first for new OBS 2.4
            binary = prj = args[0]
        elif len(args) == 2:
            prj = args[0]
            pac = args[1]
        else:
            raise oscerr.WrongArgs('Wrong number of arguments.')

        if pac is not None:
            apiurl = self.get_api_url()
            print("last entries in %s.changes :" % pac)
            link_url = makeurl(apiurl, ['source', prj, pac, "%s.changes" % pac])
            try:
               file = http_GET(link_url)
            except urllib2.HTTPError, e:
                print >>sys.stderr, 'Cannot fetch %s/%s/%s.changes: %s' % (prj, pac, pac, e)
                return
            m_list = []
            for l in file.readlines():
                # Thu Sep 13 13:52:04 CEST 2012 - mls@suse.de
                m = re.match(r"(\S.*)\s+\-\s+(\S+@\S+)", l)
                if m:
                  m_list.append(m.group(1) + " - " + m.group(2))
                  print " " + m_list[-1]
                  if len(m_list) > 9:
                    break
            print "\n(%s)" % OSC_MAINTAINER_PLUGIN_NAME

