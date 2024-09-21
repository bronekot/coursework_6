from django.core.mail.backends.smtp import EmailBackend


class CustomEmailBackend(EmailBackend):
    # Переопределяем local_hostname
    def open(self):
        if self.connection:
            return False

        connection_params = {"local_hostname": "localhost"}  # Переопределяем local_hostname
        if self.timeout is not None:
            connection_params["timeout"] = self.timeout
        if self.use_ssl:
            connection_params["context"] = self.ssl_context
        try:
            self.connection = self.connection_class(self.host, self.port, **connection_params)

            if not self.use_ssl and self.use_tls:
                self.connection.starttls(context=self.ssl_context)
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except OSError:
            if not self.fail_silently:
                raise
