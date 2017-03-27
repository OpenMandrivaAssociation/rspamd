%define rspamd_user      rspamd
%define rspamd_group     %{rspamd_user}
%define rspamd_home      %{_localstatedir}/lib/rspamd
%define rspamd_logdir    %{_localstatedir}/log/rspamd
%define rspamd_confdir   %{_sysconfdir}/rspamd
%define rspamd_pluginsdir   %{_datadir}/rspamd
%define rspamd_rulesdir   %{_datadir}/rspamd/rules
%define rspamd_wwwdir   %{_datadir}/rspamd/www

Name:		rspamd
Version:	1.5.3
Release:	1
Summary:	Rapid spam filtering system
Group:		System/Servers
License:	BSD-2-Clause
URL:		https://rspamd.com/
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(libevent)
BuildRequires:	pkgconfig(libcrypto)
BuildRequires:	pkgconfig(libssl)
BuildRequires:	pkgconfig(libpcre)
BuildRequires:  pkgconfig(lua)
BuildRequires:	pkgconfig(fann)
BuildRequires:	pkgconfig(icu-i18n)
BuildRequires:  cmake
BuildRequires:	magic-devel
BuildRequires:	perl
BuildRequires:	ragel
BuildRequires:  pkgconfig(sqlite3)
BuildRequires:	ninja
Requires(pre,postun):  rpm-helper
Source0:	https://rspamd.com/downloads/%{name}-%{version}.tar.xz
Patch1:		rspamd-1.3.5-clang.patch
#Patch2:		rspamd-1.3.5-openssl-1.1.patch
Requires:	lua-lpeg

%description
Rspamd is a rapid, modular and lightweight spam filter. It is designed to work
with big amount of mail and can be easily extended with own filters written in
lua.

%prep
%setup -q
%apply_patches

%build
# ENABLE_LUAJIT is off because of lua 5.3 vs. luajit 5.1 mismatch
%{__cmake} \
	-DCMAKE_C_OPT_FLAGS="%{optflags}" \
	-DCMAKE_INSTALL_PREFIX=%{_prefix} \
	-DCONFDIR=%{_sysconfdir}/rspamd \
	-DMANDIR=%{_mandir} \
	-DDBDIR=%{_localstatedir}/lib/rspamd \
	-DRUNDIR=%{_localstatedir}/run/rspamd \
	-DWANT_SYSTEMD_UNITS=ON \
	-DSYSTEMDDIR=%{_unitdir} \
	-DENABLE_LUAJIT=OFF \
	-DENABLE_HIREDIS=ON \
	-DLOGDIR=%{_localstatedir}/log/rspamd \
	-DEXAMPLESDIR=%{_datadir}/examples/rspamd \
	-DPLUGINSDIR=%{_datadir}/rspamd \
	-DLIBDIR=%{_libdir} \
	-DINCLUDEDIR=%{_includedir} \
	-DNO_SHARED=ON \
	-DDEBIAN_BUILD=1 \
	-DRSPAMD_GROUP=%{rspamd_group} \
	-DRSPAMD_USER=%{rspamd_user} \
	-G Ninja

ninja

%install
DESTDIR=%{buildroot} INSTALLDIRS=vendor ninja install

%{__install} -d -p -m 0755 %{buildroot}%{rspamd_home}
%{__install} -p -D -d -m 0755 %{buildroot}%{_sysconfdir}/%{name}/local.d/
%{__install} -p -D -d -m 0755 %{buildroot}%{_sysconfdir}/%{name}/override.d/

sed -i -e 's,^User=.*,User=%{rspamd_user},g' %{buildroot}%{_unitdir}/%{name}.service

%pre
%_pre_useradd %{rspamd_user} %{rspamd_home} /sbin/nologin

%postun
%_postun_userdel %{rspamd_user}
%_postun_groupdel %{rspamd_group}

%files
%{_unitdir}/%{name}.service
%{_mandir}/man8/%{name}.*
%{_mandir}/man1/rspamc.*
%{_mandir}/man1/rspamadm.*
%{_bindir}/rspamd
%{_bindir}/rspamd_stats
%{_bindir}/rspamc
%{_bindir}/rspamadm
%config(noreplace) %{rspamd_confdir}/%{name}.conf
%config(noreplace) %{rspamd_confdir}/%{name}.sysvinit.conf
%config(noreplace) %{rspamd_confdir}/composites.conf
%config(noreplace) %{rspamd_confdir}/maillist.inc
%config(noreplace) %{rspamd_confdir}/metrics.conf
%config(noreplace) %{rspamd_confdir}/mid.inc
%config(noreplace) %{rspamd_confdir}/mime_types.inc
%config(noreplace) %{rspamd_confdir}/modules.conf
%config(noreplace) %{rspamd_confdir}/statistic.conf
%config(noreplace) %{rspamd_confdir}/common.conf
%config(noreplace) %{rspamd_confdir}/logging.inc
%config(noreplace) %{rspamd_confdir}/options.inc
%config(noreplace) %{rspamd_confdir}/redirectors.inc
%config(noreplace) %{rspamd_confdir}/worker-controller.inc
%config(noreplace) %{rspamd_confdir}/worker-fuzzy.inc
%config(noreplace) %{rspamd_confdir}/worker-normal.inc
%config(noreplace) %{rspamd_confdir}/modules.d/*
%config(noreplace) %{rspamd_confdir}/rspamd.systemd.conf
%attr(-,%{rspamd_user},%{rspamd_user}) %dir %{rspamd_home}
%dir %{rspamd_rulesdir}/regexp
%dir %{rspamd_rulesdir}
%dir %{rspamd_confdir}
%dir %{rspamd_confdir}/modules.d
%dir %{rspamd_confdir}/local.d
%dir %{rspamd_confdir}/override.d
%dir %{rspamd_pluginsdir}/lua
%dir %{rspamd_pluginsdir}
%dir %{rspamd_wwwdir}
%config(noreplace) %{rspamd_confdir}/2tld.inc
%config(noreplace) %{rspamd_confdir}/surbl-whitelist.inc
%config(noreplace) %{rspamd_confdir}/spf_dkim_whitelist.inc
%config(noreplace) %{rspamd_confdir}/dmarc_whitelist.inc
%{rspamd_pluginsdir}/lua/*.lua
%{rspamd_rulesdir}/regexp/*.lua
%{rspamd_rulesdir}/*.lua
%{rspamd_wwwdir}/*
%{_libdir}/*.so
%{_datadir}/rspamd/effective_tld_names.dat
