# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.network "private_network", ip: "192.168.50.100"
  config.vm.network "forwarded_port", guest: 9966, host: 9966
  config.vm.network "forwarded_port", guest: 35729, host: 35729
  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.vm.network "forwarded_port", guest: 9200, host: 9200
  config.vm.synced_folder "..", "/CPDB", owner: "vagrant", group: "vagrant"

  config.vm.provider "virtualbox" do |vb|
    vb.memory = "2048"
  end

  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "ansible/vagrant.yml"
    ansible.host_key_checking = false
    ansible.ask_vault_pass = true
    ansible.verbose = "v"
  end
end