package Carding.APICard.controller;

import Carding.APICard.model.Tarjeta;
import Carding.APICard.service.TarjetaService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/tarjetas")
@RequiredArgsConstructor
public class TarjetaController {

    private final TarjetaService tarjetaService;

    @PostMapping
    public ResponseEntity<Tarjeta> crearTarjeta(@Valid @RequestBody Tarjeta tarjeta) {
        Tarjeta nuevaTarjeta = tarjetaService.crearTarjeta(tarjeta);
        return new ResponseEntity<>(nuevaTarjeta, HttpStatus.CREATED);
    }

    @GetMapping
    public ResponseEntity<List<Tarjeta>> obtenerTodasTarjetas() {
        List<Tarjeta> tarjetas = tarjetaService.obtenerTodasTarjetas();
        return ResponseEntity.ok(tarjetas);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Tarjeta> obtenerTarjetaPorId(@PathVariable Long id) {
        Tarjeta tarjeta = tarjetaService.obtenerTarjetaPorId(id);
        return ResponseEntity.ok(tarjeta);
    }

    @PutMapping("/{id}")
    public ResponseEntity<Tarjeta> actualizarTarjeta(
            @PathVariable Long id,
            @Valid @RequestBody Tarjeta tarjeta) {
        Tarjeta tarjetaActualizada = tarjetaService.actualizarTarjeta(id, tarjeta);
        return ResponseEntity.ok(tarjetaActualizada);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, String>> eliminarTarjeta(@PathVariable Long id) {
        tarjetaService.eliminarTarjeta(id);
        return ResponseEntity.ok(Map.of("mensaje", "Tarjeta eliminada exitosamente"));
    }

    @GetMapping("/buscar")
    public ResponseEntity<List<Tarjeta>> buscarTarjetasPorAnio(
            @RequestParam(defaultValue = "2024") Integer anio) {
        List<Tarjeta> tarjetas = tarjetaService.buscarTarjetasPorAnio(anio);
        return ResponseEntity.ok(tarjetas);
    }
}