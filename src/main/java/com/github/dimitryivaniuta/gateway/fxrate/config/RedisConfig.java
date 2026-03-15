package com.github.dimitryivaniuta.gateway.fxrate.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.serializer.GenericJackson2JsonRedisSerializer;
import org.springframework.data.redis.serializer.StringRedisSerializer;

/**
 * Configures Redis serialization for latest-rate cache entries.
 */
@Configuration
public class RedisConfig {

    /**
     * Creates a Redis template with string keys and JSON values.
     *
     * @param connectionFactory redis connection factory
     * @param objectMapper shared object mapper
     * @return configured redis template
     */
    @Bean
    public RedisTemplate<String, Object> redisTemplate(
            final RedisConnectionFactory connectionFactory,
            final ObjectMapper objectMapper) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(connectionFactory);
        template.setKeySerializer(new StringRedisSerializer());
        template.setValueSerializer(new GenericJackson2JsonRedisSerializer(objectMapper));
        template.setHashKeySerializer(new StringRedisSerializer());
        template.setHashValueSerializer(new GenericJackson2JsonRedisSerializer(objectMapper));
        return template;
    }
}
