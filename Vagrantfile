VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "hashicorp/precise32"
  config.vm.network "private_network", ip:"10.0.0.3"
  config.vm.hostname = "NETWORKAPI-WEBUI"
  #config.omnibus.chef_version = :latest
  #config.vm.provision :chef_solo do |chef|
  #end
  config.vm.provision :shell, path: "scripts/vagrant_provision.sh"
end

