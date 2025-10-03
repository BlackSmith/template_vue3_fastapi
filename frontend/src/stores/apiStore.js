import {defineStore} from 'pinia';
import api from '@/services/api'
import {camelToWords} from '@/helpers.js'

export default defineStore('apiStore', {
  state: () => ({
    openApiSchemas: {},
    openApiPaths: {},
    loading: false,
    error: null,
  }),
  persistent: true,
  actions: {

    async loadOpenApiSchemas() {
      this.loading = true;
      try {
        const response = await api.get('/openapi.json');
        this.openApiSchemas = response.data?.components?.schemas;
        this.openApiPaths = response.data?.paths;
      } catch (error) {
        this.error = 'Failed to load OpenAPI data';
        console.error(this.error)
      } finally {
        this.loading = false;
      }
    },

    getSchema(objectType) {
      if (!this.openApiSchemas) {
        throw new Error('Invalid OpenAPI data or object name not found');
      }

      objectType = objectType.replace('#/components/schemas/', '');

      // get definitions from OpenAPI
      const schema = this.openApiSchemas[objectType];

      if (!schema) {
        throw new Error(`Schema for ${objectType} not found in OpenAPI data`);
      }
      return schema
    },

    reduceObject(schema, obj) {
      if (!schema || typeof obj !== 'object' || obj === null) {
        return obj;
      }

      const reduced = {};
      for (const key in obj) {
        if (schema.properties && schema.properties[key]) {
          const propertySchema = schema.properties[key];
          const value = obj[key];

          if (propertySchema.type === 'object' && typeof value === 'object') {
            reduced[key] = this.reduceObject(propertySchema, value);
          } else if (propertySchema.type === 'array' && Array.isArray(value)) {
            reduced[key] = value.map(item =>
                propertySchema.items ? this.reduceObject(
                    !propertySchema.items['$ref'] ? propertySchema.items : this.getSchema(propertySchema.items['$ref']), item
                ) : item
            );
          } else {
            reduced[key] = value;
          }
        }
      }

      return reduced;
    },

    reduce(objectType, obj) {
      return this.reduceObject(this.getSchema(objectType), obj);
    },

    getMaxLength(objectType, attr) {
      const prop = this.getSchema(objectType)?.properties[attr]
      return prop?.maxLength || prop?.anyOf?.[0].maxLength;
    },

    isRequired(objectType, attr) {
      return this.getSchema(objectType)?.required.indexOf(attr) >= 0
    },

    getPath(objectType) {
      const valueToFind = `#/components/schemas/${objectType}`
      const key = Object.entries(this.openApiPaths).find(([key, value]) =>
          value?.post?.requestBody?.content?.['application/json']?.schema?.['$ref'].startsWith(valueToFind) ||
          value?.put?.requestBody?.content?.['application/json'].schema?.['$ref'].startsWith(valueToFind)
      )?.[0];
      return key.replace(/\{.+\}\/?/, '')
    },

    async submit(objectType, item) {
      const path = this.getPath(objectType)
      const name = camelToWords(objectType)
      console.log("Form submitted!", item, path);
      try {
        if (item?.id) {
          const ok = await api.put(
              `${path}${item.id}`,
              this.reduce(`${objectType}Update`, item)
          )
          return {
            updated: ok.data,
            notification: {
              status: 'ok',
              icon: 'mdi-content-save-check',
              text: ok.data?.name ? `The ${name} "${ok.data.name}" was saved.` : `The ${name} was saved.`,
            }
          }
        } else {
          const ok = await api.post(
              path,
              this.reduce(`${objectType}Create`, item)
          )
          return {
            created: ok.data,
            notification: {
              status: 'ok',
              icon: 'mdi-content-save-check',
              text: ok.data?.name ? `The ${name} "${ok.data.name}" was created.` : `The ${name} was created.`,
            }
          }
        }
      } catch (error) {
        console.warn(error)
        return {
          notification: {
            status: 'error',
            error: error,
            icon: 'mdi-content-save-alert-outline'
          }
        }
      }
    },

    async delete(objectType, item) {
      const path = this.getPath(objectType)
      const name = camelToWords(objectType)
      console.log("Delete!", item, path);
      try {
        const ok = await api.delete(
            `${path}${item.id}`
        )
        return {
          notification: {
            status: 'info',
            icon: 'mdi-delete-forever',
            text: item?.name ? `The ${name} "${item.name}" was deleted.` : `The ${name} was deleted.`,
          }
        }
      } catch (error) {
        console.warn(error)
        return {
          notification: {
            status: 'error',
            error: error
          }
        }
      }
    },
  }
});
