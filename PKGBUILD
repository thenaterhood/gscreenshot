# Maintainer: Nate Levesque <public at thenaterhood dawt com>
pkgname=gscreenshot
pkgver=2.0.0
pkgrel=1
epoch=
pkgdesc="A minimal GTK frontend for the scrot screenshooter"
arch=('any')
url="https://github.com/thenaterhood/gscreenshot"
license=('GPL')
groups=()
depends=("python3"
        "python-pillow"
        "scrot"
        "gtk3"
        "python-setuptools"
        "python-gobject")
makedepends=("unzip")
checkdepends=()
optdepends=()
provides=()
conflicts=()
replaces=()
backup=()
options=()
install=
changelog=
source=("https://github.com/thenaterhood/gscreenshot/archive/master.zip")
noextract=("master.zip")
md5sums=('SKIP')
validpgpkeys=()

prepare() {
        unzip $srcdir/master.zip
        cd $srcdir/gscreenshot-master
}

build() {
        echo "Nothing to build"
}

check() {
        echo "Nothing to check"
}

package() {
        echo $pkgdir
        cd $srcdir/gscreenshot-master
        python setup.py install --root="$pkgdir/" --optimize=1
        chmod +x "$pkgdir/usr/bin/gscreenshot"
}
