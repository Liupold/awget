mkdir 'tmp-for-awget'

# reference files
curl 'http://www.ovh.net/files/1Gb.dat' > 'tmp-for-awget/1Gb.dat.curl'
curl 'http://speedtest.tele2.net/100MB.zip' > 'tmp-for-awget/100MB.zip.curl'
curl 'https://speed.hetzner.de/100MB.bin' > 'tmp-for-awget/100MB.bin.curl'

python3 'tests/test_engine.py'; TEST_EXIT="$?"
rm -rf 'tmp-for-awget'
exit "$TEST_EXIT"
