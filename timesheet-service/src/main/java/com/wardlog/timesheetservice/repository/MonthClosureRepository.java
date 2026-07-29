package com.wardlog.timesheetservice.repository;

import com.wardlog.timesheetservice.entity.MonthClosure;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;
import java.util.UUID;

public interface MonthClosureRepository extends JpaRepository<MonthClosure, UUID> {

    boolean existsByDoctorIdAndYearAndMonth(UUID doctorId, int year, int month);

    Optional<MonthClosure> findByDoctorIdAndYearAndMonth(UUID doctorId, int year, int month);
}
