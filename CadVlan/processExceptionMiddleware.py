class LoggingMiddleware(object):

    def process_exception(self, request, exception):
        """ HIDE PASSWORD VALUES"""

        # Get POST value
        post_values = request.POST.copy()

        if('password' in post_values):

            # Change PASSWORD value to '*'
            post_values['password'] = '******'
            request.POST = post_values

        if('new_pass' in post_values):

            # Change NEW_PASS value to '*'
            post_values['new_pass'] = '******'
            request.POST = post_values

        if('confirm_new_password' in post_values):

            # Change CONFIRM_NEW_PASSWORD value to '*'
            post_values['confirm_new_password'] = '******'
            request.POST = post_values

        if('second_password' in post_values):

            # Change SECOND_PASSWORD value to '*'
            post_values['second_password'] = '******'
            request.POST = post_values

        # Get META value
        meta_values = request.META.copy()

        if('HTTP_NETWORKAPI_PASSWORD' in meta_values):

            # Change HTTP_NETWORKAPI_PASSWORD value to '*'
            meta_values['HTTP_NETWORKAPI_PASSWORD'] = '******'
            request.META = meta_values
