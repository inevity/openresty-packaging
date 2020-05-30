# Abstract
Build Openresty/Nginx against OpenSSl which have HTTP3 Boringssl API for QUIC using Cloudflare's Quiche impl.
使用 Cloudflare quiche（QUIC 实现）基于修改的 OpenSSL，构建 Nginx/OpenResty
* OpenSSl1.1.1g 支持 QUIC draft 27
* Cloudflare quiche master 基于 OpenSSL 构建
* Nginx/OpenResty 1.17.10 基于 OpenSSL 构建



# Build process
```
mkdir build
cd build
git clone -b nginx-1.17.10-quic-support --single-branch  https://github.com/inevity/openresty.git
git clone -b openresty-packaging-quic-support --single-branch https://github.com/inevity/openresty-packaging.git
cd openresty
make clean && make
cd ../openresty-packaging/deb
make zlib-build
sudo apt-get install ./a.deb ./a-dev.deb
make pcre-build
sudo apt-get install ./a.deb ./a-dev.deb
make opensll111-build
sudo apt-get install ./openresty-openssl111-dev_1.1.1g-1~focal1_amd64.deb ./openresty-openssl111_1.1.1g-1~focal1_amd64.deb
make opensll111-debug-build
sudo apt-get install ./openresty-openssl111-debug-dev_1.1.1g-1~focal1_amd64.deb ./openresty-openssl111-debug_1.1.1g-1~focal1_amd64.deb

make openresty-build
sudo apt-get install ./openresty_1.17.10.1rc1-1~focal1_amd64.de

make openresty-debug-build
sudo apt-get install ./openresty-debug_1.17.10.1rc1-1~focal1_amd64.deb


mkdir ~/build/http3
rsync -av /usr/local/openresty/nginx/conf http3/
rsync -av /usr/local/openresty/nginx/html http3/
rsync -av /usr/local/openresty/nginx/logs http3/
cd ~/build/http3
sudo openresty -p .
sudo openresty -p . -s reload
sudo openresty -p . -s stop
sudo openresty-debug -p .

/curl/bin/curl -vvv --http3  https://approachai.com
tail -f logs/error.log
```


# Dev Notes
##  OpesnSSL 支持 HTTP3
本质是实现 BoringSSL 的 QUIC API. 具体参见 [Akamai OpenSSL QUIC Branch](https://github.com/akamai/openssl/tree/OpenSSL_1_1_1g-quic)
讨论见 [WIP: master QUIC support #8797](https://github.com/openssl/openssl/pull/8797)
如下最后两个 patch 是针对 BoringSSL 对 QUIC 传输层的方法的修改而来的，目前支持最新 Cloudflare QUICHE.
```
ubuntu@easybubuild:~/build/openresty-packaging$ cat deb/openresty-openssl111/debian/patches/series
openssl-1.1.1c-sess_set_get_cb_yield.patch
0001-Add-support-for-BoringSSL-QUIC-APIs.patch
0002-Fix-resumption-secret.patch
0003-QUIC-Handle-EndOfEarlyData-and-MaxEarlyData.patch
0004-QUIC-Increase-HKDF_MAXBUF-to-2048.patch
0005-Fall-through-for-0RTT.patch
0006-Some-cleanup-for-the-main-QUIC-changes.patch
0007-Prevent-KeyUpdate-for-QUIC.patch
0008-Test-KeyUpdate-rejection.patch
0009-Fix-out-of-bounds-read-when-TLS-msg-is-split-up-into.patch
0001-update-quice-method.patch
fupdatesetread.patch
```
## Cloudflare QUICHE 针对 OpenSLL 编译的修改
原来 QUICHE 构建只针对 BoringSSL，这个 patch 使得基于 OpenSSL 构建成为可能。
讨论见 [WIP tls: add feature to build against OpenSSL #126](https://github.com/cloudflare/quiche/pull/126)
我的修改主要是针对最新的 BoringSSL 引入的改变，做了相应的改变。
比如 add 了 early data/0 RTT，规避了 SSL_get_peer_signature_algorithm，SSL_get_curve_id 等
```
ubuntu@easybubuild:~/build/openresty$ ls patches/0001-tls-add-feature-to-build-against-OpenSSL.patch
patches/0001-tls-add-feature-to-build-against-OpenSSL.patch
```

## OpenResty/Nginx 的 HTTP3 支持
本质需要基于 TLS1.3 和 QUICHE 提供的传输层 API 和 HTTP3 API，提供 HTTP3 实现。
核心 patch 是 Cloudflare 提供的[基于 BorignSSL 的 nginx quic patch](https://github.com/cloudflare/quiche/tree/master/extras/nginx)
nginx-1.17.10-quiche.patch 是核心 patch。
由于基于 pkgconfig 方式构建的 QUICHE，删除了这个核心 patch 对 nginx 里的 openssl 的构建的修改`auto/lib/openssl/make`， 添加了单独构建 OpenSSL 包的情况，添加了调试选项。

```
ubuntu@easybubuild:~/build/openresty$ ls patches/nginx-1.17.10-quiche* -t
patches/nginx-1.17.10-quiche-remove_opennssl_make_fix.patch  patches/nginx-1.17.10-quiche_openssldebug.patch
patches/nginx-1.17.10-quiche.patch                           patches/nginx-1.17.10-quiche_sshheader.patch
```


# Have Done
* Debain package openresty-openssl111, openresty,and debug package .

# To DO

* The QUIC draft 28
* RPM package
* Alpine image
* 0-RTT test
* test nginx with openssl dir option,which the quiche also need the openssl.
* hard coded cargo path and openssl lib path in nginx

