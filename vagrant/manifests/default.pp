# puppet manifest

# Make sure the correct directories are in the path:
Exec {
    path => [
    '/usr/local/sbin',
    '/usr/local/bin',
    '/usr/sbin',
    '/usr/bin',
    '/sbin',
    '/bin',
    ],
    logoutput => true,
}

# Refresh the catalog of repositories from which packages can be installed:
exec {'apt-get-update':
    command => 'apt-get update'
}

# make sure we have some basic tools and libraries available

package {'redis-server':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'libxslt1-dev':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'libxml2':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'libxml2-dev':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'build-essential':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'python3-dev':
    ensure => installed,
    require => Exec['apt-get-update']
}
package {'python-pip':
    ensure => installed,
    require => Package['python3-dev']
}

package {'python-setuptools':
    ensure => installed,
    require => Package['python3-dev']
}

package {'git':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'unzip':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'curl':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'wget':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'libcurl4-openssl-dev':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'openssl':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'zlib1g-dev':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'libsqlite3-dev':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'sqlite3':
    ensure => latest,
    require => Exec['apt-get-update'],
}

# ntp - prevent time drift
package {'ntp':
    ensure => latest,
    require => Exec['apt-get-update'],
}

service {'ntp':
    ensure => running,
    enable => true,
    hasrestart => true,
    require => Package['ntp'],
}

# Install Postgresql
package {'postgresql':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'postgresql-contrib':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'libpq-dev':
    ensure => latest,
    require => Exec['apt-get-update'],
}

# Set up Postgres DB/user for project
exec {'drop-project-db':
    require => Package['postgresql'],
    command => 'psql -d postgres -c "DROP DATABASE IF EXISTS academic_integrity_tool_v2"',
    user => 'postgres',
    group => 'postgres',
    logoutput => true,
}
exec {'drop-existing-project-user':
    require => Exec['drop-project-db'],
    command => 'psql -d postgres -c "DROP USER IF EXISTS academic_integrity_tool_v2"',
    user => 'postgres',
    group => 'postgres',
    logoutput => true,
}

exec {'create-project-user':
    require => Exec['drop-existing-project-user'],
    command => 'psql -d postgres -c "CREATE USER academic_integrity_tool_v2 WITH PASSWORD \'academic_integrity_tool_v2\'"',
    user => 'postgres',
    group => 'postgres',
    logoutput => true,
}
exec {'create-project-db':
    require => Exec['create-project-user'],
    command => 'psql -d postgres -c "CREATE DATABASE academic_integrity_tool_v2 WITH OWNER academic_integrity_tool_v2"',
    user => 'postgres',
    group => 'postgres',
    logoutput => true,
}

# Generate secure.py
exec {'generate-secure.py':
    provider => 'shell',
    user => 'vagrant',
    group => 'vagrant',
    command => 'cp /home/vagrant/academic_integrity_tool_v2/academic_integrity_tool_v2/settings/secure.py.example /home/vagrant/academic_integrity_tool_v2/academic_integrity_tool_v2/settings/secure.py',
    require => [File['/home/vagrant/academic_integrity_tool_v2'], ]
}

# Ensure github.com ssh public key is in the .ssh/known_hosts file so
# pip won't try to prompt on the terminal to accept it
file {'/home/vagrant/.ssh':
    ensure => directory,
    mode => 0700,
}

exec {'known_hosts':
    provider => 'shell',
    user => 'vagrant',
    group => 'vagrant',
    command => 'ssh-keyscan github.com >> /home/vagrant/.ssh/known_hosts',
    unless => 'grep -sq github.com /home/vagrant/.ssh/known_hosts',
    require => [ File['/home/vagrant/.ssh'], ],
}

file {'/home/vagrant/.ssh/known_hosts':
    ensure => file,
    mode => 0744,
    require => [ Exec['known_hosts'], ],
}

# install virtualenv and virtualenvwrapper - depends on pip

# Note, hardcoding version of pip packages because of the following error:
#Error: /Stage[main]/Main/Package[virtualenv]/ensure: change from 15.1.0 to latest failed: Could not get latest version: HTTP-Error: 403 Must access using HTTPS instead of HTTP
package {'virtualenv':
    ensure => '15.1.0',
    provider => 'pip',
    require => [ Package['python-pip'], ],
}

package {'virtualenvwrapper':
    ensure => '4.8.2',
    provider => 'pip',
    require => [ Package['python-pip'], ],
}

file {'/etc/profile.d/venvwrapper.sh':
    ensure => file,
    content => 'source `which virtualenvwrapper.sh`',
    mode => '755',
    require => Package['virtualenvwrapper'],
}

# Create a symlink from ~/academic_integrity_tool_v2 to /vagrant as a convenience for the developer
file {'/home/vagrant/academic_integrity_tool_v2':
    ensure => link,
    target => '/vagrant',
}

# Create a virtualenv for academic_integrity_tool_v2
exec {'create-virtualenv':
    provider => 'shell',
    user => 'vagrant',
    group => 'vagrant',
    require => [ Package['virtualenvwrapper'], File['/home/vagrant/academic_integrity_tool_v2'], Exec['known_hosts'], Exec['create-project-db']],
    environment => ["HOME=/home/vagrant","WORKON_HOME=/home/vagrant/.virtualenvs"],
    command => '/vagrant/vagrant/venv_bootstrap.sh',
    creates => '/home/vagrant/.virtualenvs/academic_integrity_tool_v2',
}

# set the DJANGO_SETTINGS_MODULE environment variable
file_line {'add DJANGO_SETTINGS_MODULE env to postactivate':
    ensure => present,
    line => 'export DJANGO_SETTINGS_MODULE=academic_integrity_tool_v2.settings.local',
    path => '/home/vagrant/.virtualenvs/academic_integrity_tool_v2/bin/postactivate',
    require => Exec['create-virtualenv'],
}

file_line {'add DJANGO_SETTINGS_MODULE env to postdeactivate':
    ensure => present,
    line => 'unset DJANGO_SETTINGS_MODULE',
    path => '/home/vagrant/.virtualenvs/academic_integrity_tool_v2/bin/postdeactivate',
    require => Exec['create-virtualenv'],
}

# Active this virtualenv upon login
file {'/home/vagrant/.bash_profile':
    owner => 'vagrant',
    content => '
echo "Activating python virtual environment \"academic_integrity_tool_v2\""
workon academic_integrity_tool_v2
        
# Show git repo branch at bash prompt
parse_git_branch() {
    git branch 2> /dev/null | sed -e \'/^[^*]/d\' -e \'s/* \(.*\)/(\1)/\'
}
PS1="${debian_chroot:+($debian_chroot)}\u@\h:\w\$(parse_git_branch) $ "
    ',
    require => Exec['create-virtualenv'],
}

