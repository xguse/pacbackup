#!/usr/bin/python

import argparse

import pyalpm
from pycman import config

import os

# import pygit2

from version import __version__

"""
This module is a part of PacBackup. It backs up the package list along with a scipt 
allowing easy recovery.
"""


def sanitize_path(path):
  return os.path.abspath(os.path.expanduser(path))

def pkg_info_str(pkg):
  return str(pkg.name + "\t" + pkg.version + "\t" + pkg.db.name)

class PacBackup:
  def __init__(self, options):
    self.handle = config.init_with_config_and_options(options)
    self.backup_file_path = sanitize_path(options.backup_config)
    self.container = os.path.abspath(os.path.join(self.backup_file_path, os.pardir))
    print(self.backup_file_path)
    print(self.container)
    self.verbosity = options.verbose

  def retrieve_pkg_lists(self):
    syncpkgs = set()
    for db in self.handle.get_syncdbs():
      syncpkgs |= set(p.name for p in db.pkgcache)

    db = self.handle.get_localdb()

    self.official_pkg = [x for x in db.pkgcache if x.reason == pyalpm.PKG_REASON_EXPLICIT and x.name in syncpkgs]
    self.aur_pkg    = [x for x in db.pkgcache if x.reason == pyalpm.PKG_REASON_EXPLICIT and x.name not in syncpkgs]

    if self.verbosity :
      print("Official : ")
      for pkg in self.official_pkg:
        print("\t" + pkg_info_str(pkg))

      print("AUR : ")
      for pkg in self.aur_pkg:
        print("\t" + pkg_info_str(pkg))

  def prepare_backup_folder(self):
    os.mkdir(self.container)
    # pygit2.init_repository(self.container, False)


  def backup_pkg_lists(self):
    if not os.path.exists(self.container):
      self.prepare_backup_folder()

    with open(self.backup_file_path, 'w+') as backup:
      backup.write("# Generated by PacBackup "+__version__+"\n")
      backup.write("[official repositories]\n")
      for pkg in self.official_pkg:
        backup.write(pkg_info_str(pkg) + "\n")
      backup.write("\n")
      backup.write("[AUR]\n")
      for pkg in self.aur_pkg:
        backup.write(pkg_info_str(pkg) + "\n")


def main():

  parser = config.make_parser(description='Backs-up the list of pacman-installed packages on the system.', 
    prog = 'pacbackup')

  group = parser.add_argument_group("Backup options")
  group.add_argument('--backup-config', metavar='<path>', default='~/.pacbackup/pkglist', 
    help = "specifies the backup file location, default : ~/.pacbackup/pkglist")

  backup = PacBackup(parser.parse_args())
  backup.retrieve_pkg_lists()
  backup.backup_pkg_lists()


if __name__ == '__main__':
  main()