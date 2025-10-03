<script>
import {defineComponent} from "vue";
import {formatDate} from '@/helpers.js'
import Page from "@/components/page.vue";
import Table from "@/components/table.vue";
import UsergroupForm from './forms/usergroupForm.vue'


export default defineComponent({
  components: {Page, Table, UsergroupForm},
  props: {},
  data() {
    return {
      selected: null,
      selectedEvent: null,
      gridApi: null,
      rowData: null,
      columnDefs: [
        {headerName: 'ID', field: 'id', maxWidth: 75},
        {headerName: 'Name', field: 'name'},
        {headerName: 'Description', field: 'description'},
        {headerName: 'Keycloak role', field: 'realm_role'},
        {
          headerName: 'Created',
          field: 'created_at',
          valueFormatter: (params) => {
            return params.value ? formatDate(params.value) : '';
          }
        }
      ],
    }
  },
  computed: {
    isDetailShown: {
      get() {
        return this.selected !== null;
        ;
      },
      set(value) {
        if (!value) {
          this.selected = null;
        }
      }
    }
  },
  methods: {
    async onGridReady(params) {
      const response = await this.$api.get('/api/users-groups/');
      this.rowData = response.data;
      this.gridApi = params.api;
    },
    async doSelect(event) {
      if (event.data?.id && this.selected?.id === event.data?.id) {
        this.selected = null;
      } else {
        this.selected = event.data;
        this.selectedEvent = event
      }
    },
    cancelDone(item) {
      this.selected = null;
    },
    updateDone(item) {
      this.gridApi.refreshCells({rowNodes: [this.selectedEvent.node]})
      this.selected = null;
    },
    createDone(item) {
      if (!this.rowData) {
        this.rowData = []
      }
      this.rowData.push(item)
      this.selected = null;
      this.$nextTick(() => {
        const rowIndex = this.rowData.length - 1;
        this.gridApi.ensureIndexVisible(rowIndex);
      });
    },
    deleteDone(item) {
      this.rowData = this.rowData.filter(row => row.id !== item.id);
      this.selected = null;
    }
  }
})
</script>

<template>
  <page v-model="isDetailShown">
    <template #buttons>
      <v-btn @click="selected = {}">Add</v-btn>
    </template>


    <template #panel>
      <usergroup-form :selected="selected"
                      @canceled="cancelDone"
                      @updated="updateDone"
                      @created="createDone"
                      @deleted="deleteDone"
      />
    </template>

    <Table
        @ready="onGridReady"
        @select="doSelect"
        :columnDefs="columnDefs"
        :rowData="rowData"
    ></Table>
  </page>
</template>
