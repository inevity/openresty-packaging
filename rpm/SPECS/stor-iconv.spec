Name:               stor-iconv
Version:            1.15
Release:            0%{?dist}
Summary:            library for iconv

Group:              System Environment/Libraries

License:            BSD
URL:                https://www.gnu.org/software/libiconv/
Source0:            https://ftp.gnu.org/gnu/libiconv/libiconv-%{version}.tar.gz

BuildRoot:          %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:      libtool

AutoReqProv:        no

%define iconv_prefix     /usr/local/stor-openresty/iconv

%description
The iconv library for use by Openresty ONLY


%package devel
Summary:            Development files for %{name}
Group:              Development/Libraries
Requires:           %{name} = %{version}-%{release}


%description devel
Development files for library for iconv


%prep
%setup -q -n libiconv-%{version}


%build
./configure --prefix=%{iconv_prefix}

make %{?_smp_mflags}


%install
make install DESTDIR=%{buildroot}
rm -rf %{buildroot}/%{iconv_prefix}/bin/*
rm -rf %{buildroot}/%{iconv_prefix}/share
rm -rf %{buildroot}/%{iconv_prefix}/lib/*.la


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%attr(0755,root,root) %{iconv_prefix}/lib/*.so*
%attr(0755,root,root) %{iconv_prefix}/lib/*.alias


%files devel
%defattr(-,root,root,-)
%{iconv_prefix}/lib/*.a
%{iconv_prefix}/include/*.h


%changelog
* Tue Feb 21 2017 Chen Tao
- initial build for libiconv 1.15.
