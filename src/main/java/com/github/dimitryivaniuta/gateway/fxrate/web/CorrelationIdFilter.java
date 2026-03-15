package com.github.dimitryivaniuta.gateway.fxrate.web;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.UUID;
import org.slf4j.MDC;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

/**
 * Adds a correlation identifier to every request for log tracing and client diagnostics.
 */
@Component
public class CorrelationIdFilter extends OncePerRequestFilter {

    /** Public correlation header name. */
    public static final String CORRELATION_ID_HEADER = "X-Correlation-Id";

    /** MDC key used by logging frameworks. */
    public static final String MDC_KEY = "correlationId";

    /**
     * Applies the correlation identifier to the request lifecycle.
     *
     * @param request HTTP request
     * @param response HTTP response
     * @param filterChain downstream chain
     * @throws ServletException on servlet errors
     * @throws IOException on I/O errors
     */
    @Override
    protected void doFilterInternal(
            final HttpServletRequest request,
            final HttpServletResponse response,
            final FilterChain filterChain) throws ServletException, IOException {
        String correlationId = request.getHeader(CORRELATION_ID_HEADER);
        if (correlationId == null || correlationId.isBlank()) {
            correlationId = UUID.randomUUID().toString();
        }

        MDC.put(MDC_KEY, correlationId);
        response.setHeader(CORRELATION_ID_HEADER, correlationId);
        response.setHeader("Cache-Control", "no-store");
        try {
            filterChain.doFilter(request, response);
        } finally {
            MDC.remove(MDC_KEY);
        }
    }
}
