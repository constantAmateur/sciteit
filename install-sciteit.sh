#!/bin/bash -e
#Matthew Young, Sciteit

# configuration that doesn't change much
SCITEIT_REPO=git://github.com/constantAmateur/sciteit.git
I18N_REPO=git://github.com/constantAmateur/sciteit-i18n.git
SCIHTMLATEX_REPO=git://github.com/constantAmateur/scihtmlatex.git
APTITUDE_OPTIONS="-y" # limit bandwidth: -o Acquire::http::Dl-Limit=100"

# don't blunder on if an error occurs
set -e

# validate some assumptions of the script
if [ $(id -u) -ne 0 ]; then
    echo "ERROR: Must be run with root privileges."
    exit 1
fi

source /etc/lsb-release
if [ "$DISTRIB_ID" != "Ubuntu" ]; then
    echo "ERROR: Unknown distribution $DISTRIB_ID. Only Ubuntu is supported."
    exit 1
fi

if [ "$DISTRIB_RELEASE" != "11.04" ]; then
    echo "ERROR: Only Ubuntu 11.04 is supported."
    exit 1
fi

# get configured
echo "Welcome to the sciteit install script!"

SCITEIT_USER=${SUDO_USER:-sciteit}
read -ei $SCITEIT_USER -p "What user should sciteit run as? " SCITEIT_USER

SCITEIT_HOME=/home/$SCITEIT_USER
read -ei $SCITEIT_HOME -p "What directory should it be installed in? " SCITEIT_HOME

echo "Beginning installation. This may take a while..."
echo

# create the user if non-existent
if ! id $SCITEIT_USER> /dev/null; then
    adduser --system $SCITEIT_USER
fi

# add some external ppas for packages
DEBIAN_FRONTEND=noninteractive apt-get install $APTITUDE_OPTIONS aptitude python-software-properties
apt-add-repository ppa:jason-alioth/reddit

# pin the ppa
cat <<HERE > /etc/apt/preferences.d/reddit
Package: *
Pin: release o=LP-PPA-jason-alioth-reddit
Pin-Priority: 600
HERE

# grab the new ppas' package listings
aptitude update

# install prerequisites
DEBIAN_FRONTEND=noninteractive aptitude install $APTITUDE_OPTIONS python-dev python-setuptools python-imaging python-pycaptcha python-mako python-nose python-decorator python-formencode python-pastescript python-beaker python-webhelpers python-amqplib python-pylibmc python-pycountry python-psycopg2 python-cssutils python-beautifulsoup python-sqlalchemy cython python-pybabel python-tz python-boto python-lxml python-pylons python-pycassa python-recaptcha gettext make optipng uwsgi uwsgi-core uwsgi-plugin-python nginx git-core python-profiler memcached postgresql postgresql-client curl daemontools daemontools-run rabbitmq-server cassandra python-bcrypt python-snudown
#Setup extra things we need that reddit doesn't
aptitude install $APTITUDE_OPTIONS python-feedparser
#Setup latex seperately as it's huge
aptitude install $APTITUDE_OPTIONS texlive-full

#Install the good version of java
apt-get install python-software-properties
add-apt-repository ppa:ferramroberto/java
apt-get update
aptitude install $APTITUDE_OPTIONS sun-java6-jre sun-java6-plugin 
#If you want to actually use this, you'll have to change it with
#sudo update-alternatives --config java

# grab the source
if [ ! -d $SCITEIT_HOME ]; then
    mkdir $SCITEIT_HOME
    chown $SCITEIT_USER $SCITEIT_HOME
fi

cd $SCITEIT_HOME

if [ ! -d $SCITEIT_HOME/sciteit ]; then
    sudo -u $SCITEIT_USER git clone $SCITEIT_REPO
fi

if [ ! -d $SCITEIT_HOME/sciteit-i18n ]; then
    sudo -u $SCITEIT_USER git clone $I18N_REPO
fi

if [ ! -d $SCITEIT_HOME/scihtmlatex ]; then
    sudo -u $SCITEIT_USER git clone $SCIHTMLATEX_REPO
fi

#Install scihtmlatex
if [ ! -d /tmp/htmlatex ]; then
    mkdir -p /tmp/htmlatex
fi
cd $SCITEIT_HOME/scihtmlatex
python setup.py install

#Setup solr to run...
if [ ! -d /home/solr/apache-solr-1.4.1 ]; then
    mkdir -p /home/solr
    cd /home/solr
    if [ ! -f apache-solr-1.4.1.tgz ]; then
        wget http://www.trieuvan.com/apache//lucene/solr/1.4.1/apache-solr-1.4.1.tgz
    fi
    tar -xvf apache-solr-1.4.1.tgz
    cp $SCITEIT_HOME/sciteit/config/solr/schema.xml /home/solr/apache-solr-1.4.1/example/solr/conf/
    cp $SCITEIT_HOME/sciteit/config/solr/solrconfig.xml /home/solr/apache-solr-1.4.1/example/solr/conf/
    chown -R sciteit:sciteit /home/solr
fi

# wait a bit to make sure all the servers come up
sleep 30

# configure cassandra
if ! echo | cassandra-cli -h localhost -k sciteit > /dev/null 2>&1; then
    echo "create keyspace sciteit;" | cassandra-cli -h localhost -B
fi

echo "create column family permacache with column_type = 'Standard' and comparator = 'BytesType';" | cassandra-cli -B -h localhost -k sciteit || true

# set up postgres
IS_DATABASE_CREATED=$(sudo -u postgres psql -t -c "SELECT COUNT(1) FROM pg_catalog.pg_database WHERE datname = 'sciteit';")

if [ $IS_DATABASE_CREATED -ne 1 ]; then
    cat <<PGSCRIPT | sudo -u postgres psql
CREATE DATABASE sciteit WITH ENCODING = 'utf8';
CREATE USER sciteit WITH PASSWORD 'password';
PGSCRIPT
fi

sudo -u postgres psql sciteit < $SCITEIT_HOME/sciteit/sql/functions.sql

# set up rabbitmq
if ! rabbitmqctl list_vhosts | egrep "^/$"
then
    rabbitmqctl add_vhost /
fi

if ! rabbitmqctl list_users | egrep "^sciteit"
then
    rabbitmqctl add_user sciteit sciteit
fi

rabbitmqctl set_permissions -p / sciteit ".*" ".*" ".*"

#Clean everything out first
cd $SCITEIT_HOME/sciteit/r2
make clean
cd $SCITEIT_HOME/sciteit-i18n/
make clean

# run the sciteit setup script
cd $SCITEIT_HOME/sciteit/r2
sudo -u $SCITEIT_USER make pyx # generate the .c files from .pyx
sudo -u $SCITEIT_USER python setup.py build
python setup.py develop

# run the i18n setup script
cd $SCITEIT_HOME/sciteit-i18n/
sudo -u $SCITEIT_USER python setup.py build
python setup.py develop
sudo -u $SCITEIT_USER make

# do the r2 build after languages are installed
cd $SCITEIT_HOME/sciteit/r2
sudo -u $SCITEIT_USER make

# install the daemontools runscripts
cd $SCITEIT_HOME/sciteit/r2
if [ ! -L run.ini ]; then
    sudo -u $SCITEIT_USER ln -s example.ini run.ini
fi

#Remove cassandra and memcached
update-rc.d -f cassandra remove
update-rc.d -f memcached remove
#Stop them
/etc/init.d/cassandra stop
/etc/init.d/memcached stop

ln -s $SCITEIT_HOME/sciteit/srv/{comments_q,commentstree_q,scraper_q,vote_link_q,vote_comment_q,search_q,cassandra,memcached,solr} /etc/service/ || true
/sbin/start svscan || true
#Change owner...
sudo chown -R ${SCITEIT_USER}:${SCITEIT_USER} ${SCITEIT_HOME}/sciteit/srv/

# set up uwsgi
cat >/etc/uwsgi/apps-available/sciteit.ini <<UWSGI
[uwsgi]
; master / uwsgi protocol configuration
plugins = python
master = true
master-as-root = true
vacuum = true
limit-post = 512000
buffer-size = 8096
uid = $SCITEIT_USER
chdir = $SCITEIT_HOME/sciteit/r2
socket = /tmp/sciteit.sock
chmod-socket = 666

; worker configuration
lazy = true
max-requests = 10000
processes = 1

; app configuration
paste = config:$SCITEIT_HOME/sciteit/r2/run.ini
UWSGI

if [ ! -L /etc/uwsgi/apps-enabled/sciteit.ini ]; then
    ln -s /etc/uwsgi/apps-available/sciteit.ini /etc/uwsgi/apps-enabled/sciteit.ini
fi

/etc/init.d/uwsgi start

# set up nginx
cat >/etc/nginx/sites-available/sciteit <<NGINX
include uwsgi_params;
uwsgi_param SCRIPT_NAME "";

server {
    listen 8081;

    location / {
        uwsgi_pass unix:///tmp/sciteit.sock;

        gzip on;
        gzip_vary on;
        gzip_proxied any;
        gzip_min_length 100;
        gzip_comp_level 4;
        gzip_types text/plain text/css text/javascript text/xml application/json text/csv application/x-javascript application/xml application/xml+rss;
    }
}
NGINX

if [ ! -L /etc/nginx/sites-enabled/sciteit ]; then
    ln -s /etc/nginx/sites-available/sciteit /etc/nginx/sites-enabled/sciteit
fi
/etc/init.d/nginx restart

# install the crontab
CRONTAB=$(mktemp)

crontab -u $SCITEIT_USER -l > $CRONTAB || true

cat >>$CRONTAB <<CRON
# m h  dom mon dow   command
*/5   *   *   *   *    $SCITEIT_HOME/sciteit/scripts/rising.sh
*/4   *   *   *   *    $SCITEIT_HOME/sciteit/scripts/send_mail.sh
*/3   *   *   *   *    $SCITEIT_HOME/sciteit/scripts/broken_things.sh
#1     *   *   *   *    $SCITEIT_HOME/sciteit/scripts/update_promos.sh
0    3    *   *   *    $SCITEIT_HOME/sciteit/scripts/update_rss.sh
#30     *   *   *   *    $SCITEIT_HOME/sciteit/scripts/reindex_all.sh
0    23   *   *   *    $SCITEIT_HOME/sciteit/scripts/update_sciteits.sh
30   23   *   *   *    $SCITEIT_HOME/sciteit/scripts/update_sr_names.sh
CRON
crontab -u $SCITEIT_USER $CRONTAB
rm $CRONTAB

# done!
cd $SCITEIT_HOME
echo "Done installing sciteit!"
#If using python2.7
#To make sure indexing doesn't poop out...
#Make sure to edit line 1068 (def _escape_cdata) of /usr/lib/python2.7/xml/etree/ElementTree.py to...
#return text.decode(encoding).encode(encoding,"xmlcharrefreplace")
#Change the uwsgi plugin from "python" to "python27"
#Initialize the db
#paster shell run.ini
#from r2.models.populatedb import *
#initialize()

