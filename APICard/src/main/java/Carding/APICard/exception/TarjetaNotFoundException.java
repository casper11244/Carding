package Carding.APICard.exception;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;

@ResponseStatus(HttpStatus.NOT_FOUND)
public class TarjetaNotFoundException extends RuntimeException {

    public TarjetaNotFoundException(String mensaje) {
        super(mensaje);
    }

    public TarjetaNotFoundException(String mensaje, Throwable causa) {
        super(mensaje, causa);
    }
}