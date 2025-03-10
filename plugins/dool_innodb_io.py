### Author: Dag Wieers <dag$wieers,com>, Ming-Hung Chen <minghung.chen@gmail.com>

global mysql_options
mysql_options = os.getenv('DOOL_MYSQL')

class dool_plugin(dool):
    def __init__(self):
        self.name = 'innodb io ops '
        self.nick = ('rea', 'wri', 'syn')
        self.vars = ('read', 'write', 'sync')
        self.type = 'f'
        self.width = 3
        self.scale = 1000

    def check(self):
        if os.access('/usr/bin/mysql', os.X_OK):
            try:
                self.stdin, self.stdout, self.stderr = dpopen('/usr/bin/mysql -n %s' % mysql_options)
            except IOError:
                raise Exception('Cannot interface with MySQL binary')
            return True
        raise Exception('Needs MySQL binary')

    def extract(self):
        try:
            self.stdin.write(b'show engine innodb status\G\n')
            line = matchpipe(self.stdout, '.*OS file reads,.*')

            if line:
                l = line.split()
                self.set2['read'] = int(l[0])
                self.set2['write'] = int(l[4])
                self.set2['sync'] = int(l[8])

            for name in self.vars:
                self.val[name] = (self.set2[name] - self.set1[name]) * 1.0 / elapsed

            if step == op.delay:
                self.set1.update(self.set2)

        except IOError as e:
            if op.debug > 1: print('%s: lost pipe to mysql, %s' % (self.filename, e))
            for name in self.vars: self.val[name] = -1

        except Exception as e:
            if op.debug > 1: print('%s: exception' % (self.filename, e))
            for name in self.vars: self.val[name] = -1

# vim:ts=4:sw=4:et
