package Carding.APICard.service;

import Carding.APICard.model.Tarjeta;
import java.util.List;

public interface TarjetaService {

    Tarjeta crearTarjeta(Tarjeta tarjeta);

    List<Tarjeta> obtenerTodasTarjetas();

    Tarjeta obtenerTarjetaPorId(Long id);

    Tarjeta actualizarTarjeta(Long id, Tarjeta tarjeta);

    void eliminarTarjeta(Long id);

    List<Tarjeta> buscarTarjetasPorAnio(Integer anio);
}