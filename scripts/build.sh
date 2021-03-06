# This script should be called from within Hudson

cd $WORKSPACE
VENV=$WORKSPACE/venv

echo "Starting build..."

# Make sure there's no old pyc files around.
find . -name '*.pyc' | xargs rm

if [ ! -d "$VENV/bin" ]; then
  echo "No virtualenv found.  Making one..."
  virtualenv --no-site-packages $VENV
fi

source $VENV/bin/activate

pip install -q -r requirements.txt

cat > settings_local.py <<SETTINGS
from settings import *
ROOT_URLCONF = 'workspace.urls'
LOG_LEVEL = logging.ERROR
DATABASES['default']['TEST_CHARSET'] = 'utf8'
DATABASES['default']['TEST_COLLATION'] = 'utf8_general_ci'
SETTINGS

echo "Starting tests..."
export FORCE_DB='yes sir'
coverage run manage.py test --noinput --logging-clear-handlers --with-xunit
coverage xml $(find apps lib -name '*.py')

echo "Building documentation..."
cd docs
make clean dirhtml SPHINXOPTS='-q'
cd $WORKSPACE

echo 'shazam!'
