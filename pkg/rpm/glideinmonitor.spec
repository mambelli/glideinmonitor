# Modified version starting from the setuptools generated one
# https://docs.fedoraproject.org/en-US/packaging-guidelines/Python/
# Wheels packaging is possible but not recommended
# https://fedoraproject.org/wiki/PythonWheels

# Release Candidates NVR format
#%define release 0.1.rc1
# Official Release NVR format
#%define release 1

#%global version __GWMS_RPM_VERSION__
#%global release __GWMS_RPM_RELEASE__

%define name glideinmonitor
%define version 0.1
%define unmangled_version %{version}
%define release 0.1.rc1

Summary: GlideinMonitor Web Server and Indexer
Name: %{name}
Version: %{version}
Release: %{release}%{?dist}
License: Fermitools Software Legal Information (Modified BSD License)
Group: Development/Libraries
#BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Prefix: %{_prefix}
BuildArch: noarch
Vendor: GlideinWMS team <glideinwms-support@fnal.gov>
Url: https://github.com/glideinWMS/glideinmonitor

Source0: %{name}-%{unmangled_version}.tar.gz

%global srcname glideinmonitor

%global config_file %{_sysconfdir}/%{srcname}
%global glideinmonitor_dir %{_localstatedir}/lib/glideinmonitor
%global archive_dir %{glideinmonitor_dir}/archive
%global upload_dir %{glideinmonitor_dir}/upload
%global processing_dir %{glideinmonitor_dir}/processing
%global db_dir %{glideinmonitor_dir}/db
# DB defined in config file (may be local or remote)
# %global db_dir %{_localstatedir}/lib/glideinmonitor/db
# using also:
# /usr/sbin %{_sbindir} , /var/lib %{_sharedstatedir}, /usr/share %{_datadir}, cron dir, ?
%global systemddir %{_prefix}/lib/systemd/system


Requires: python3
# Should Flask be required or pip-installed?
#Requires: python3-flask
BuildRequires: python3-devel
%description
GlideinMonitor is a package for archiving and serving the log files written by
the Glidein of GlideinWMS (Glidein Workload Management System).

glideinmonitor-webserver
glideinmonitor-indexer


%package monolith
Summary:        GlideinMonitor Web Server, Indexer and DB
Group:          System Environment/Daemons
#Provides:       glideinmonitor-monolith = %{version}-%{release}
#Obsoletes:      glideinmonitor-monolith < %{version}-%{release}
Requires: glideinmonitor-common = %{version}-%{release}
Requires: glideinmonitor-indexer = %{version}-%{release}
Requires: glideinmonitor-webserver = %{version}-%{release}
# Requires: glideinmonitor-db = %{version}-%{release}
%description monolith
GlideinMonitor is a package for archiving and serving the log files written by
the Glidein of GlideinWMS (Glidein Workload Management System).
This package installs all the components.

%package common
Summary:        GlideinMonitor common components
Group:          System Environment/Daemons
#Provides:       glideinmonitor-common = %{version}-%{release}
#Obsoletes:      glideinmonitor-common < %{version}-%{release}
Requires(pre): /usr/sbin/useradd
%description common
GlideinMonitor is a package for archiving and serving the log files written by
the Glidein of GlideinWMS (Glidein Workload Management System).
This package installs common elements.

%package indexer
Summary:        GlideinMonitor Web Server, Indexer and DB
Group:          System Environment/Daemons
#Provides:       glideinmonitor-monolith = %{version}-%{release}
#Obsoletes:      glideinmonitor-monolith < %{version}-%{release}
Requires: glideinmonitor-common = %{version}-%{release}
%description indexer
GlideinMonitor is a package for archiving and serving the log files written by
the Glidein of GlideinWMS (Glidein Workload Management System).
This package installs the indexer, that sorts and prepares the archive.

%package webserver
Summary:        GlideinMonitor Web Server, Indexer and DB
Group:          System Environment/Daemons
#Provides:       glideinmonitor-monolith = %{version}-%{release}
#Obsoletes:      glideinmonitor-monolith < %{version}-%{release}
Requires: glideinmonitor-common = %{version}-%{release}
%description webserver
GlideinMonitor is a package for archiving and serving the log files written by
the Glidein of GlideinWMS (Glidein Workload Management System).
This package installs the webserver, that serves the log archive.

# TODO: is a db package needed?

%prep

#%autosetup -n %{srcname}-%{version}
%setup -n %{name}-%{unmangled_version}

%build
%{__python3} setup.py build

#install -D bin/stashcp %{buildroot}%{_bindir}/stashcp
#install -D -m 0644 bin/caches.json %{buildroot}%{_datarootdir}/stashcache/caches.json

%install
%{__python3} setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
install -d $RPM_BUILD_ROOT%{archive_dir}
install -d $RPM_BUILD_ROOT%{upload_dir}
install -d $RPM_BUILD_ROOT%{processing_dir}
install -d $RPM_BUILD_ROOT%{db_dir}
echo %{archive_dir} >> INSTALLED_FILES
echo %{upload_dir} >> INSTALLED_FILES
echo %{processing_dir} >> INSTALLED_FILES
echo %{db_dir} >> INSTALLED_FILES
# System startup and cron
install -d $RPM_BUILD_ROOT/%{systemddir}
install -m 0644 pkg/rpm/glideinmonitor-indexer.service $RPM_BUILD_ROOT/%{systemddir}/
install -m 0644 pkg/rpm/glideinmonitor-webserver.service $RPM_BUILD_ROOT/%{systemddir}/
install -m 0644 pkg/rpm/glideinmonitor-indexer.timer $RPM_BUILD_ROOT/%{systemddir}/
install -d $RPM_BUILD_ROOT/%{_sbindir}
install -m 0755 pkg/rpm/glideinmonitor-indexer $RPM_BUILD_ROOT/%{_sbindir}/
install -m 0755 pkg/rpm/glideinmonitor-webserver $RPM_BUILD_ROOT/%{_sbindir}/


%pre common
# Add the "gmonitor" user and group if they do not exist
getent group gmonitor >/dev/null || groupadd -r gmonitor
getent passwd gmonitor >/dev/null || \
       useradd -r -g gmonitor -d /var/lib/glideinmonitor -c "GlideinMonitor user" -s /sbin/nologin gmonitor
# If the gmonitor user already exists make sure it is part of gmonitor group
usermod --append --groups gmonitor gmonitor >/dev/null


%post indexer
# $1 = 1 - Installation
# $1 = 2 - Upgrade
# Source: http://www.ibm.com/developerworks/library/l-rpm2/
systemctl daemon-reload

%post webserver
# $1 = 1 - Installation
# $1 = 2 - Upgrade
# Source: http://www.ibm.com/developerworks/library/l-rpm2/
pip3 install flask
systemctl daemon-reload
# Protecting from failure in case it is not running/installed
#/sbin/service httpd reload > /dev/null 2>&1 || true


%preun indexer
# $1 = 0 - Action is uninstall
# $1 = 1 - Action is upgrade
if [ "$1" = "0" ] ; then
    systemctl daemon-reload
fi
#if [ "$1" = "0" ]; then
#    # Remove the symlinks if added
#    # A lot of files are generated, but rpm won't delete those
#
##    rm -rf %{glideinmonitor_dir}/*
##    rm -rf %{_localstatedir}/log/glideinmonitor/*
#fi

%preun webserver
if [ "$1" = "0" ] ; then
    systemctl daemon-reload
fi


%clean
rm -rf $RPM_BUILD_ROOT


%files common -f INSTALLED_FILES
%defattr(-,root,root)
%attr(-, gmonitor, gmonitor) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/glideinmonitor.conf

%files indexer
%attr(0755, root, root) %{_sbindir}/glideinmonitor-indexer
%attr(0644, root, root) %{systemddir}/glideinmonitor-indexer.service
%attr(0644, root, root) %{systemddir}/glideinmonitor-indexer.timer
%attr(-, gmonitor, gmonitor) %dir %{_sysconfdir}/glideinmonitor-indexer
%attr(-, gmonitor, gmonitor) %dir %{_sysconfdir}/glideinmonitor-indexer/filter.d
%attr(-, gmonitor, gmonitor) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/glideinmonitor-indexer.conf


%files webserver
%attr(0755, root, root) %{_sbindir}/glideinmonitor-webserver
%attr(0644, root, root) %{systemddir}/glideinmonitor-webserver.service
%attr(-, gmonitor, gmonitor) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/glideinmonitor-webserver.conf

#%files
#%{_bindir}/stashcp
#%{_datarootdir}/stashcache/caches.json
#%{_datarootdir}/stashcache/README-caches


%changelog

