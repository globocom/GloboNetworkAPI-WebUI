# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''


error_messages = {
    'required':             u'Este campo é obrigatório.',
    'max_length':           u'Este campo tem que ter no máximo %(limit_value)s caracteres.',
    'min_length':           u'Este campo tem que ter no mínimo %(limit_value)s caracteres.',
    'invalid_choice':       u'Opção inválida selecionada.',
    'can_not_remove_all':   u'Não foi possível excluir nenhum dos itens selecionados.',
    'can_not_remove':       u'Não foi possível excluir alguns dos itens selecionados: %s.',
    'can_not_remove_error': u'A exclusão dos itens selecionados não foi concluído.',
    'select_one':           u'Nenhum item foi selecionado.',
}

auth_messages = {
    'user_not_authorized':  u'Usuário não autorizado para acessar/executar está operação.',
    'user_invalid':         u'Usuário e/ou senha incorretos.',
    '404':                  u'Página não encontrada: [URL: %s]',
    '500':                  u'Ocorreu um erro ao executar sua ação, contate o Administrador do sistema.',
    'user_email_invalid':   u'Usuário e/ou email incorretos.',
    'email_success':        u'Nova senha enviada com sucesso.'
}

script_messages = {
    'success_remove':       u'Todos os roteiros selecionados foram excluídos com sucesso.',
    'success_insert':       u'Roteiro incluído com sucesso.',
    'error_equal_name':     u'Roteiro com o nome %s já cadastrado.',
}

script_type_messages = {
    'success_remove':       u'Todos os tipos de roteiros selecionados foram excluídos com sucesso.',
    'success_insert':       u'Tipo de Roteiro incluído com sucesso.',
    'error_equal_name':     u'Tipo de roteiro com nome %s já cadastrado',
}

equip_access_messages = {
    'success_remove':       u'Todos os acessos selecionados foram excluídos com sucesso.',
    'success_insert':       u'Acesso incluído com sucesso.',
    'already_association':  u'Equipamento e Protocolo já associados',
    'invalid_equip_acess':  u'Equipamento Acesso inválido',
    'success_edit':         u'Acesso alterado com sucesso.',
    'success_remove':       u'Todos os acesso de equipamentos foram excluídos com sucesso.',
    'no_equip':             u'Selecione um equipamento.',
}

equip_script_messages = {
    'success_remove':       u'Todos os roteiros selecionados foram excluídos com sucesso.',
    'success_insert':       u'Roteiro associado com sucesso.',
    'error_equal_ass':      u'O roteiro selecionado já está associado à este equipamento.',
}

equip_interface_messages = {
    'success_remove':       u'Todas as interfaces selecionadas foram excluídas com sucesso.',
}