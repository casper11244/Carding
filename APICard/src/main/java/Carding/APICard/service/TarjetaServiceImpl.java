package Carding.APICard.service;

import Carding.APICard.exception.TarjetaNotFoundException;
import Carding.APICard.model.Tarjeta;
import Carding.APICard.repository.TarjetaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional
public class TarjetaServiceImpl implements TarjetaService {

    private final TarjetaRepository tarjetaRepository;

    @Override
    public Tarjeta crearTarjeta(Tarjeta tarjeta) {
        if (tarjetaRepository.existsByNumero(tarjeta.getNumero())) {
            throw new IllegalArgumentException("Ya existe una tarjeta con ese número");
        }
        return tarjetaRepository.save(tarjeta);
    }

    @Override
    @Transactional(readOnly = true)
    public List<Tarjeta> obtenerTodasTarjetas() {
        return tarjetaRepository.findAll();
    }

    @Override
    @Transactional(readOnly = true)
    public Tarjeta obtenerTarjetaPorId(Long id) {
        return tarjetaRepository.findById(id)
                .orElseThrow(() -> new TarjetaNotFoundException("Tarjeta no encontrada con ID: " + id));
    }

    @Override
    public Tarjeta actualizarTarjeta(Long id, Tarjeta tarjetaActualizada) {
        Tarjeta tarjetaExistente = obtenerTarjetaPorId(id);

        // Verificar si el nuevo número ya existe y pertenece a otra tarjeta
        if (!tarjetaExistente.getNumero().equals(tarjetaActualizada.getNumero()) &&
                tarjetaRepository.existsByNumero(tarjetaActualizada.getNumero())) {
            throw new IllegalArgumentException("Ya existe otra tarjeta con ese número");
        }

        tarjetaExistente.setNumero(tarjetaActualizada.getNumero());
        tarjetaExistente.setMes(tarjetaActualizada.getMes());
        tarjetaExistente.setAnio(tarjetaActualizada.getAnio());
        tarjetaExistente.setCcv(tarjetaActualizada.getCcv());

        return tarjetaRepository.save(tarjetaExistente);
    }

    @Override
    public void eliminarTarjeta(Long id) {
        Tarjeta tarjeta = obtenerTarjetaPorId(id);
        tarjetaRepository.delete(tarjeta);
    }

    @Override
    @Transactional(readOnly = true)
    public List<Tarjeta> buscarTarjetasPorAnio(Integer anio) {
        return tarjetaRepository.findByAnioGreaterThanEqual(anio);
    }
}