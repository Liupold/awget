TMP_DIR='tmp-for-awget'
USER_AGENT='Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0'
mkdir -p "$TMP_DIR"


# reference files
curl --user-agent "$USER_AGENT" 'http://www.ovh.net/files/1Gb.dat' > "$TMP_DIR/1Gb.dat.curl"
curl --user-agent "$USER_AGENT" 'http://speedtest.tele2.net/100MB.zip' > "$TMP_DIR/100MB.zip.curl"
curl --user-agent "$USER_AGENT" 'https://speed.hetzner.de/100MB.bin' > "$TMP_DIR/100MB.bin.curl"

python -m pip install requests parameterized python-magic
python 'tests/test_engine.py'; TEST_EXIT="$?"
rm -rf 'tmp-for-awget'
exit "$TEST_EXIT"
