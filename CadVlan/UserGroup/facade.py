def represents_int(s):

    try:
        int(s)
        return True
    except ValueError:
        return False


def get_vips_request(client, search, pagination, id_obj):

    fields = ['id', 'name']

    if pagination is not None and search is not None:
        data_search = {
            'start_record': pagination.start_record,
            'end_record': pagination.end_record,
            'asorting_cols': pagination.asorting_cols,
            'searchable_columns': pagination.searchable_columns,
            'custom_search': pagination.custom_search or '',
            'extends_search': [
                {
                    'id': search
                } if represents_int(search) else {},
                {
                    'name__icontains': search
                }
            ]
        }

        vips = client.create_api_vip_request() \
            .search(search=data_search, fields=fields)

        return {'total': vips['total'], 'objs': vips['vips']}

    else:
        vips = client.create_api_vip_request() \
            .get([id_obj], fields=fields)

        return {'total': len(vips['vips']), 'objs': vips['vips']}


def get_server_pools(client, search, pagination, id_obj):

    fields = ['id', 'identifier']

    if pagination is not None and search is not None:
        data_search = {
            'start_record': pagination.start_record,
            'end_record': pagination.end_record,
            'asorting_cols': pagination.asorting_cols,
            'searchable_columns': pagination.searchable_columns,
            'custom_search': pagination.custom_search or '',
            'extends_search': [
                {
                    'id': search
                } if represents_int(search) else {},
                {
                    'identifier__icontains': search
                }
            ]
        }

        pools = client.create_api_pool() \
            .search(search=data_search, fields=fields)

        return {'total': pools['total'], 'objs': pools['server_pools']}

    else:
        pools = client.create_api_pool() \
            .get([id_obj], fields=fields)

        return {'objs': pools['server_pools']}


def get_vlans(client, search, pagination, id_obj):

    fields = ['id', 'name']

    if pagination is not None and search is not None:
        data_search = {
            'start_record': pagination.start_record,
            'end_record': pagination.end_record,
            'asorting_cols': pagination.asorting_cols,
            'searchable_columns': pagination.searchable_columns,
            'custom_search': pagination.custom_search or '',
            'extends_search': [
                {
                    'id': search
                } if represents_int(search) else {},
                {
                    'num_vlan': search
                } if represents_int(search) else {},
                {
                    'nome__icontains': search
                }
            ]
        }

        vlans = client.create_api_vlan() \
            .search(search=data_search, fields=fields)

        return {'total': vlans['total'], 'objs': vlans['vlans']}

    else:
        vlans = client.create_api_vlan() \
            .get([id_obj], fields=fields)

        return {'objs': vlans['vlans']}
